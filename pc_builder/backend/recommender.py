import re
from pc_builder.backend.pricing import price_of
from pc_builder.database.products import CATEGORIES, products_in

def guess_use_cases(user_text):
    text = user_text.lower()
    use_cases = []
    if re.search("office|excel|coding|work|business|study", text):
        use_cases.append("office")
    if re.search("game|gaming|edit|editing|render|stream|youtube|premiere", text):
        use_cases.append("gaming")
        use_cases.append("creator")
    if re.search("home|movie|browsing|school|family|daily", text):
        use_cases.append("home")
    return use_cases

def guess_budget_range(user_text):
    text = user_text.lower().replace(",", "")
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*(lakh|lac|l|k|thousand)?", text)
    values = []
    for number, unit in matches:
        value = float(number)
        if unit in ["lakh", "lac", "l"]:
            value = value * 100000
        elif unit in ["k", "thousand"]:
            value = value * 1000
        elif value < 1000:
            continue
        if value >= 25000:
            values.append(clean_budget(value))
    if len(values) >= 2:
        return min(values[0], values[1]), max(values[0], values[1])
    if len(values) == 1:
        budget = values[0]
        return clean_budget(budget * 0.90), clean_budget(budget * 1.10)
    return None

def clean_budget(amount):
    rounded = round(amount / 5000) * 5000
    return int(max(25000, min(250000, rounded)))

def product_score(product, use_cases):
    return sum(product[use_case] for use_case in use_cases) / len(use_cases)

def fuzzy_ratio(value, target):
    ratio = value / target
    if ratio >= 1:
        return min(1.25, ratio)
    return ratio

def needed_processor_capability(use_cases, budget, cpu_priority):
    target = 60
    if "gaming" in use_cases:
        target = max(target, 84)
    if "creator" in use_cases:
        target = max(target, 90)
    if "office" in use_cases:
        target = max(target, 68)
    if budget > 200000:
        target = max(target, 94)
    if cpu_priority == "Strong processor":
        target = target + 8
    if cpu_priority == "Save money on processor":
        target = target - 8
    return min(100, max(45, target))

def processor_fuzzy_score(processor, use_cases, budget, cpu_priority):
    target = needed_processor_capability(use_cases, budget, cpu_priority)
    capability_fit = fuzzy_ratio(processor["capability"], target) * 100
    task_fit = product_score(processor, use_cases)
    price_penalty = price_of(processor) / max(1, budget) * 45
    return capability_fit * 0.55 + task_fit * 0.45 - price_penalty

def gpu_fuzzy_score(graphics_card, use_cases, budget, gpu_need):
    if gpu_need == "No dedicated GPU needed":
        target_speed = 20
    elif "creator" in use_cases:
        target_speed = 88
    elif "gaming" in use_cases:
        target_speed = 82
    else:
        target_speed = 35
    if budget > 200000 and gpu_need != "No dedicated GPU needed":
        target_speed = max(target_speed, 94)
    speed_fit = fuzzy_ratio(graphics_card["speed"], target_speed) * 100
    task_fit = product_score(graphics_card, use_cases)
    price_penalty = price_of(graphics_card) / max(1, budget) * 35
    return speed_fit * 0.6 + task_fit * 0.4 - price_penalty

def product_allowed(product, preferences, budget):
    category = product["category"]
    if category == "RAM":
        allowed_sizes = [32] if budget > 200000 else preferences["ram_sizes"]
        if product["gb"] not in allowed_sizes:
            return False
        if preferences["ram_type"] != "Any" and product["ram_type"] != preferences["ram_type"]:
            return False
    if category == "ROM / Storage":
        allowed_storage = preferences["storage_sizes"]
        if budget > 200000:
            allowed_storage = [size for size in allowed_storage if size >= 1024]
        if product["storage_gb"] not in allowed_storage:
            return False
    if category == "Graphics Card":
        if preferences["gpu_need"] == "No dedicated GPU needed":
            return price_of(product) == 0
        return product["brand"] == "AMD"
    if category == "Wi-Fi Card" and not preferences["include_wifi"]:
        return False
    return True

def is_compatible(processor, motherboard, ram, graphics_card, wifi_card, power_supply, cabinet):
    if processor["socket"] != motherboard["socket"]:
        return False
    if ram["ram_type"] != motherboard["ram_type"]:
        return False
    if motherboard["size"] not in cabinet["supported_sizes"]:
        return False
    if processor["socket"] == "SNAPDRAGON-X" and wifi_card is not None:
        return False
    estimated_watts = processor["wattage"] + graphics_card["wattage"] + 110
    return power_supply["capacity"] >= estimated_watts * 1.35

def find_part(parts, category):
    for part in parts:
        if part["category"] == category:
            return part
    return None

def calculate_build_score(parts, use_cases, total_price, min_budget, max_budget, preferences):
    target_budget = (min_budget + max_budget) / 2
    processor = find_part(parts, "Processor")
    graphics_card = find_part(parts, "Graphics Card")
    motherboard = find_part(parts, "Motherboard")
    ram = find_part(parts, "RAM")
    storage = find_part(parts, "ROM / Storage")
    power_supply = find_part(parts, "Power Supply")
    cabinet = find_part(parts, "Cabinet")
    wifi_card = find_part(parts, "Wi-Fi Card")
    score = sum(product_score(part, use_cases) for part in parts)
    score += processor_fuzzy_score(processor, use_cases, target_budget, preferences["cpu_priority"]) * 1.4
    score += gpu_fuzzy_score(graphics_card, use_cases, target_budget, preferences["gpu_need"]) * 1.2
    score += 100 - abs(target_budget - total_price) / 1000

    if preferences["motherboard_spend"] == "Save money on motherboard":
        if motherboard["tier"] == "budget":
            score += 35
        if motherboard["tier"] == "premium":
            score -= 35
    if preferences["psu_quality"]:
        score += power_supply["quality"] * 0.35
    if preferences["case_quality"]:
        score += cabinet["airflow"] * 0.35
    if preferences["ram_priority"]:
        score += ram["gb"] * 2
    if preferences["less_storage"]:
        score -= price_of(storage) / 400
    if wifi_card is not None:
        score += wifi_card["wifi_rank"] * 0.25
    return score

def find_best_pc(use_cases, min_budget, max_budget, preferences):
    target_budget = (min_budget + max_budget) / 2
    best_build = None
    best_score = -10**9
    processors = products_in("Processor")
    processors.sort(
        key=lambda processor: processor_fuzzy_score(
            processor, use_cases, target_budget, preferences["cpu_priority"]
        ),
        reverse=True,
    )
    for processor in processors:
        for motherboard in products_in("Motherboard"):
            for ram in products_in("RAM"):
                if not product_allowed(ram, preferences, max_budget):
                    continue
                for storage in products_in("ROM / Storage"):
                    if not product_allowed(storage, preferences, max_budget):
                        continue
                    for graphics_card in products_in("Graphics Card"):
                        if not product_allowed(graphics_card, preferences, max_budget):
                            continue
                        wifi_options = products_in("Wi-Fi Card") if preferences["include_wifi"] else [None]
                        for wifi_card in wifi_options:
                            for power_supply in products_in("Power Supply"):
                                for cabinet in products_in("Cabinet"):
                                    if not is_compatible(
                                        processor,
                                        motherboard,
                                        ram,
                                        graphics_card,
                                        wifi_card,
                                        power_supply,
                                        cabinet,
                                    ):
                                        continue
                                    parts = [
                                        processor,
                                        motherboard,
                                        ram,
                                        storage,
                                        graphics_card,
                                        power_supply,
                                        cabinet,
                                    ]
                                    if wifi_card is not None:
                                        parts.append(wifi_card)
                                    total_price = sum(price_of(part) for part in parts)
                                    if total_price > max_budget:
                                        continue
                                    score = calculate_build_score(
                                        parts,
                                        use_cases,
                                        total_price,
                                        min_budget,
                                        max_budget,
                                        preferences,
                                    )
                                    if total_price < min_budget:
                                        score -= 20
                                    if score > best_score:
                                        best_score = score
                                        best_build = {"parts": parts, "total_price": total_price}

    if best_build is None:
        best_build = find_cheapest_pc(preferences, max_budget)
    best_build["alternatives"] = find_alternatives(best_build, use_cases, max_budget, preferences)
    return best_build

def find_cheapest_pc(preferences, budget):
    backup_preferences = preferences.copy()
    backup_preferences["gpu_need"] = "No dedicated GPU needed"
    backup_preferences["include_wifi"] = False
    cheapest = None
    cheapest_price = 10**9
    for processor in products_in("Processor"):
        for motherboard in products_in("Motherboard"):
            for ram in products_in("RAM"):
                if not product_allowed(ram, backup_preferences, budget):
                    continue
                for storage in products_in("ROM / Storage"):
                    if not product_allowed(storage, backup_preferences, budget):
                        continue
                    for graphics_card in products_in("Graphics Card"):
                        if not product_allowed(graphics_card, backup_preferences, budget):
                            continue
                        for power_supply in products_in("Power Supply"):
                            for cabinet in products_in("Cabinet"):
                                if not is_compatible(
                                    processor, motherboard, ram, graphics_card, None, power_supply, cabinet
                                ):
                                    continue
                                parts = [processor, motherboard, ram, storage, graphics_card, power_supply, cabinet]
                                total_price = sum(price_of(part) for part in parts)
                                if total_price < cheapest_price:
                                    cheapest_price = total_price
                                    cheapest = {"parts": parts, "total_price": total_price}
    return cheapest

def replace_part(parts, category, new_part):
    return [new_part if part["category"] == category else part for part in parts]

def test_build_is_compatible(parts):
    return is_compatible(
        find_part(parts, "Processor"),
        find_part(parts, "Motherboard"),
        find_part(parts, "RAM"),
        find_part(parts, "Graphics Card"),
        find_part(parts, "Wi-Fi Card"),
        find_part(parts, "Power Supply"),
        find_part(parts, "Cabinet"),
    )

def find_alternatives(build, use_cases, budget, preferences):
    alternatives = {}
    for category in CATEGORIES:
        selected_part = find_part(build["parts"], category)
        if selected_part is None:
            continue
        price_without_selected = build["total_price"] - price_of(selected_part)
        options = []
        for option in products_in(category):
            if option["name"] == selected_part["name"]:
                continue
            if not product_allowed(option, preferences, budget):
                continue
            if price_without_selected + price_of(option) > budget * 1.18:
                continue
            test_parts = replace_part(build["parts"], category, option)
            if not test_build_is_compatible(test_parts):
                continue
            options.append(option)
        options.sort(
            key=lambda product: product_score(product, use_cases) / max(1, price_of(product)),
            reverse=True,
        )
        alternatives[category] = options[:2]
    return alternatives
