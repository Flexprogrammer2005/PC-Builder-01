from urllib.parse import quote_plus

import streamlit as st

from pc_builder.backend.pricing import price_range, rupees
from pc_builder.backend.recommender import (
    find_best_pc,
    find_part,
    gpu_fuzzy_score,
    guess_budget_range,
    guess_use_cases,
    processor_fuzzy_score,
)
from pc_builder.database.products import PRODUCTS
from pc_builder.frontend.theme import apply_theme


def image_url_for(part):
    search_words = {
        "Processor": "amd processor chip",
        "Motherboard": "computer motherboard",
        "RAM": "computer ram memory",
        "ROM / Storage": "nvme ssd storage",
        "Graphics Card": "amd radeon graphics card",
        "Wi-Fi Card": "pcie wifi card",
        "Power Supply": "computer power supply",
        "Cabinet": "computer pc case",
    }
    query = quote_plus(search_words.get(part["category"], part["name"]))
    return f"https://source.unsplash.com/700x420/?{query}"


def search_link(site, product_name):
    query = quote_plus(product_name)
    links = {
        "Amazon India": f"https://www.amazon.in/s?k={query}",
        "MDComputers": f"https://mdcomputers.in/index.php?route=product/search&search={query}",
        "PrimeABGB": f"https://www.primeabgb.com/?s={query}&post_type=product",
        "Photos": f"https://www.google.com/search?tbm=isch&q={query}",
    }
    return links[site]


def show_part_card(part, alternatives):
    with st.container(border=True):
        st.subheader(part["category"])
        st.image(image_url_for(part), caption=f"{part['category']} reference photo")
        st.write(f"**{part['name']}**")
        st.write(f"Estimated price range: {price_range(part)}")
        st.caption(part["details"])

        if part["category"] == "Processor":
            st.progress(part["capability"] / 100, text=f"Processor capability: {part['capability']}/100")
        if part["category"] == "Graphics Card":
            st.progress(part["speed"] / 100, text=f"GPU speed/capability: {part['speed']}/100")

        if alternatives:
            st.write("Alternative options:")
            for option in alternatives:
                st.write(f"- {option['name']} - {price_range(option)}")
        else:
            st.write("No close alternative in this budget.")

        link_col1, link_col2, link_col3, link_col4 = st.columns(4)
        with link_col1:
            st.link_button("Amazon", search_link("Amazon India", part["name"]))
        with link_col2:
            st.link_button("MDComputers", search_link("MDComputers", part["name"]))
        with link_col3:
            st.link_button("PrimeABGB", search_link("PrimeABGB", part["name"]))
        with link_col4:
            st.link_button("Photos", search_link("Photos", part["name"]))


def get_preferences(budget):
    st.subheader("Detailed requirements")

    cpu_priority = st.radio(
        "Processor requirement",
        ["Balanced processor", "Strong processor", "Save money on processor"],
        horizontal=True,
    )
    motherboard_spend = st.radio(
        "Motherboard spending",
        ["Balanced motherboard", "Save money on motherboard", "Premium motherboard"],
        horizontal=True,
    )

    if budget > 200000:
        st.info("Budget is above ₹2,00,000, so RAM is locked to 32GB.")
        ram_sizes = [32]
    else:
        ram_sizes = st.multiselect(
            "RAM size allowed",
            [8, 16, 32],
            default=[16, 32],
            format_func=lambda size: f"{size}GB",
        )
        if not ram_sizes:
            ram_sizes = [16]

    ram_type = st.selectbox("RAM generation", ["Any", "DDR5", "DDR4"])

    if budget > 200000:
        st.info("Budget is above ₹2,00,000, so 256GB and 512GB storage are hidden.")
        storage_sizes = [1024, 2048]
    else:
        storage_sizes = st.multiselect(
            "ROM / storage size allowed",
            [256, 512, 1024, 2048],
            default=[512, 1024],
            format_func=lambda size: "1TB" if size == 1024 else "2TB" if size == 2048 else f"{size}GB",
        )
        if not storage_sizes:
            storage_sizes = [512]

    return {
        "cpu_priority": cpu_priority,
        "motherboard_spend": motherboard_spend,
        "ram_sizes": ram_sizes,
        "ram_type": ram_type,
        "storage_sizes": storage_sizes,
        "ram_priority": st.checkbox("I need fire RAM / more memory performance"),
        "less_storage": st.checkbox("Less ROM/storage is okay"),
        "psu_quality": st.checkbox("I want a stronger power supply"),
        "case_quality": st.checkbox("I want a better airflow cabinet"),
        "include_wifi": st.checkbox("Add Wi-Fi card, Wi-Fi 6E or better"),
        "gpu_need": st.radio(
            "Graphics card requirement",
            ["AMD dedicated GPU", "No dedicated GPU needed"],
            horizontal=True,
        ),
    }


def run_app():
    st.set_page_config(page_title="PC Builder India", layout="wide")
    apply_theme()

    hero_text, hero_image = st.columns([1.1, 0.9], vertical_alignment="center")
    with hero_text:
        st.markdown(
            """
            <div class="hero-copy">
              <div class="hero-kicker">PC Builder India</div>
              <h1>Build a sharper PC for your budget.</h1>
              <div class="hero-subtext">
                Pick the job, budget range, RAM, storage, processor priority,
                Wi-Fi, PSU and case needs. The builder checks compatibility and
                gives alternatives with shopping links.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with hero_image:
        st.image(
            "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?auto=format&fit=crop&w=1200&q=80",
            caption="Reference setup",
            use_container_width=True,
        )

    st.write("")
    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Catalog parts", len(PRODUCTS))
    metric2.metric("GPU policy", "AMD only")
    metric3.metric("Wi-Fi", "6E+")

    with st.expander("Where this data comes from"):
        st.write(
            "The current app uses a starter product database written in Python. "
            "The prices are estimated ranges, not live scraped prices."
        )
        st.write(
            "The product names are based on common AMD Ryzen, Snapdragon, Radeon, "
            "Wi-Fi 6E/Wi-Fi 7, PSU, cabinet, RAM, and SSD categories. "
            "Use the shopping buttons on each part to check the current live price."
        )
        st.write(
            "For a production version, the next step is replacing the PRODUCTS list "
            "with live store APIs or a backend price scraper."
        )

    user_text = st.text_area(
        "What should your PC do?",
        placeholder="Example: I want a gaming and video editing PC around 85000",
    )

    st.write("Choose one or more:")
    wants_office = st.checkbox("Office")
    wants_gaming = st.checkbox("Gaming / Video Editing")
    wants_home = st.checkbox("Home")

    budget_col1, budget_col2 = st.columns(2)
    with budget_col1:
        min_budget = st.number_input(
            "Minimum budget in rupees",
            min_value=25000,
            max_value=250000,
            value=70000,
            step=5000,
        )
    with budget_col2:
        max_budget = st.number_input(
            "Maximum budget in rupees",
            min_value=25000,
            max_value=250000,
            value=90000,
            step=5000,
        )

    guessed_range = guess_budget_range(user_text)
    if guessed_range is not None:
        min_budget, max_budget = guessed_range
        st.info(f"Budget range detected from your text: {rupees(min_budget)} to {rupees(max_budget)}")

    if min_budget > max_budget:
        min_budget, max_budget = max_budget, min_budget
        st.warning("Minimum budget was higher than maximum budget, so I swapped them.")

    target_budget = (min_budget + max_budget) / 2

    use_cases = []
    if wants_office:
        use_cases.append("office")
    if wants_gaming:
        use_cases.append("gaming")
        use_cases.append("creator")
    if wants_home:
        use_cases.append("home")
    for use_case in guess_use_cases(user_text):
        if use_case not in use_cases:
            use_cases.append(use_case)
    if not use_cases:
        use_cases = ["home"]

    preferences = get_preferences(max_budget)

    if st.button("Build My PC"):
        build = find_best_pc(use_cases, min_budget, max_budget, preferences)
        st.header("Recommended PC Build")
        st.write(f"Budget range used: {rupees(min_budget)} to {rupees(max_budget)}")
        st.metric("Estimated midpoint total", rupees(build["total_price"]))
        st.write(
            "Real checkout price can change by shop, sale, stock, delivery, and card offer. "
            "Use the shop buttons on each part before buying."
        )

        if build["total_price"] < min_budget:
            st.warning("This build is below your lower bound because the selected requirements do not need more spending.")
        if build["total_price"] > max_budget:
            st.warning("This build is above your upper bound because the requirements are too tight.")

        processor = find_part(build["parts"], "Processor")
        graphics_card = find_part(build["parts"], "Graphics Card")
        st.write(
            f"Processor fuzzy fit: {processor_fuzzy_score(processor, use_cases, target_budget, preferences['cpu_priority']):.1f}"
        )
        st.write(
            f"GPU fuzzy fit: {gpu_fuzzy_score(graphics_card, use_cases, target_budget, preferences['gpu_need']):.1f}"
        )

        col1, col2 = st.columns(2)
        for index, part in enumerate(build["parts"]):
            alternatives = build["alternatives"].get(part["category"], [])
            with col1 if index % 2 == 0 else col2:
                show_part_card(part, alternatives)
                st.divider()

    st.divider()
    st.caption(
        "Photo previews are reference images. Shopping buttons open live search pages so users can compare actual price and availability."
    )
