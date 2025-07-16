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
        if cat_sel in categories:
            cat_name = categories[cat_sel][1]
        else:
            cat_name = cat_sel
        links = links_data.get(cat_name, [])
        # Build ordered menu options (list of (key, (label, value)))
        menu_options = []
        idx = 1
        for item in links:
            if isinstance(item, dict):
                if "name" in item and "url" in item:
                    menu_options.append(
                        (str(idx), (item["name"], ("link", item["url"])))
                    )
                    idx += 1
                elif len(item) == 1:
                    subcat, sublinks = next(iter(item.items()))
                    menu_options.append((str(idx), (subcat, ("submenu", sublinks))))
                    idx += 1
        menu_options.append(("0", ("Back", None)))
        # Build dict for show_menu
        show_menu_dict = {k: (label, val) for k, (label, val) in menu_options}
        while True:
            link_sel = show_menu(
                f"{cat_name} Links", show_menu_dict, header_color=Mocha.lavender
            )
            if link_sel is None or link_sel == "0":
                break
            sel_key = None
            if isinstance(link_sel, str) and link_sel in show_menu_dict:
                sel_key = link_sel
            elif isinstance(link_sel, tuple):
                for k, v in show_menu_dict.items():
                    if isinstance(v, tuple) and v[1] == link_sel:
                        sel_key = k
                        break
            if sel_key is None or sel_key == "0":
                break
            label, val = show_menu_dict[sel_key]
            if val is None:
                break
            if isinstance(val, tuple) and val[0] == "link":
                url = val[1]
                open_link(url)
                continue
            elif isinstance(val, tuple) and val[0] == "submenu":
                subcat = label
                sublinks = val[1]
                sublink_options = {
                    str(i + 1): (subitem["name"], subitem["url"])
                    for i, subitem in enumerate(sublinks)
                    if isinstance(subitem, dict)
                    and "name" in subitem
                    and "url" in subitem
                }
                sublink_options["0"] = ("Back", None)
                while True:
                    sub_sel = show_menu(
                        f"{subcat} Links",
                        sublink_options,
                        header_color=Mocha.lavender,
                    )
                    if sub_sel is None or sub_sel == "0":
                        break
                    sub_key = None
                    if isinstance(sub_sel, str) and sub_sel in sublink_options:
                        sub_key = sub_sel
                    elif isinstance(sub_sel, str):
                        for k, v in sublink_options.items():
                            if v[1] == sub_sel:
                                open_link(sub_sel)
                                sub_key = k
                                break
                        if sub_key is not None:
                            continue
                    elif isinstance(sub_sel, tuple):
                        for k, v in sublink_options.items():
                            if v == sub_sel:
                                sub_key = k
                                break
                    if sub_key is None or sub_key == "0":
                        break
                    url = sublink_options[sub_key][1]
                    open_link(url)
                    continue


def personal_links_menu():
    links_data = load_links(PERSONAL_LINKS_PATH, default=[])
    # Ensure links_data is a list
    if isinstance(links_data, dict):
        # Convert dict to list of its values if possible, or start empty
        links_data = list(links_data.values()) if links_data else []
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
    from dataset_forge.utils.printing import print_error

    while True:
        key = show_menu("🔗 Links", options, header_color=Mocha.lavender)
        print(f"DEBUG: key={key!r}, type={type(key)}")
        if key is None or key == "0":
            break
        action = options.get(key, (None, None))[1]
        print(f"DEBUG: action={action!r}, type={type(action)}")
        if callable(action):
            action()
        else:
            print_error(
                f"Selected action is not callable: {action!r} (type={type(action)})"
            )


links_menu.__menu_options__ = {
    "1": ("🌐 Community Links", community_links_menu),
    "2": ("🔗 Personal Links", personal_links_menu),
    "0": ("⬅️  Back", None),
}
