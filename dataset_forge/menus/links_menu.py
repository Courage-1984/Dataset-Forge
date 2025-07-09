import os
import json
import webbrowser
from dataset_forge.utils.menu import show_menu
from dataset_forge.utils.printing import print_info
from dataset_forge.utils.color import Mocha

CONFIGS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "configs"
)
COMMUNITY_LINKS_PATH = os.path.join(CONFIGS_DIR, "_example_community_links.json")
PERSONAL_LINKS_PATH = os.path.join(CONFIGS_DIR, "personal_links.json")


def load_links(path, default=None):
    if not os.path.exists(path):
        return default or {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_links(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def open_link(url):
    print_info(f"Opening: {url}")
    webbrowser.open(url)


def community_links_menu():
    links_data = load_links(COMMUNITY_LINKS_PATH, default={})
    if not links_data:
        print_info(
            "No community links found. Please add them to _example_community_links.json."
        )
        return
    categories = {str(i + 1): (cat, cat) for i, cat in enumerate(links_data.keys())}
    categories["0"] = ("Back", None)
    while True:
        cat_sel = show_menu(
            "Community Links - Categories", categories, header_color=Mocha.lavender
        )
        if cat_sel is None or cat_sel == "0":
            break
        # If show_menu returns the category name directly, use it; otherwise, look it up
        if cat_sel in categories:
            cat_name = categories[cat_sel][1]
        else:
            cat_name = cat_sel
        links = links_data.get(cat_name, [])
        link_options = {
            str(i + 1): (item["name"], item["url"]) for i, item in enumerate(links)
        }
        link_options["0"] = ("Back", None)
        while True:
            link_sel = show_menu(
                f"{cat_name} Links", link_options, header_color=Mocha.lavender
            )
            if link_sel is None or link_sel == "0":
                break
            # If show_menu returns the key, look up the URL; if it returns the URL directly, use it
            if link_sel in link_options:
                url = link_options[link_sel][1]
            else:
                url = link_sel
            open_link(url)


def personal_links_menu():
    links_data = load_links(PERSONAL_LINKS_PATH, default=[])
    options = {
        str(i + 1): (item["name"], item["url"]) for i, item in enumerate(links_data)
    }
    options["A"] = ("Add New Link", "add")
    options["0"] = ("Back", None)
    while True:
        key = show_menu("Personal Links", options, header_color=Mocha.lavender)
        if key is None or key == "0":
            break
        if key == "A":
            name = input("Enter link name: ").strip()
            url = input("Enter link URL: ").strip()
            if name and url:
                links_data.append({"name": name, "url": url})
                save_links(PERSONAL_LINKS_PATH, links_data)
                print_info(f"Added link: {name} -> {url}")
                options = {
                    str(i + 1): (item["name"], item["url"])
                    for i, item in enumerate(links_data)
                }
                options["A"] = ("Add New Link", "add")
                options["0"] = ("Back", None)
            else:
                print_info("Name and URL cannot be empty.")
        else:
            url = options[key][1]
            open_link(url)


def links_menu():
    options = links_menu.__menu_options__
    while True:
        action = show_menu("Links Menu", options, header_color=Mocha.lavender)
        if callable(action):
            action()
            continue
        if action is None or action == "0":
            break
        func = options[action][1]
        if func:
            func()


links_menu.__menu_options__ = {
    "1": ("Community Links", community_links_menu),
    "2": ("Personal Links", personal_links_menu),
    "0": ("Back", None),
}
