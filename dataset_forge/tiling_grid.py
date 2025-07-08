import os
from tqdm import tqdm
import numpy as np
from numpy.random import randint, shuffle
from dataset_forge.image_ops import get_image_size
from dataset_forge.io_utils import is_image_file


# --- Tiling Functions ---
def lin_tile(input_folder, img_list, tile_size, number_tiles=None):
    if number_tiles is None:
        number_tiles = 10000
    img_dict = {}
    list_index = []
    for img_name in tqdm(img_list, desc="Tile generation"):
        try:
            w, h = get_image_size(os.path.join(input_folder, img_name))
        except Exception:
            continue
        if w < tile_size or h < tile_size:
            continue
        x_cords = np.arange(0, w // tile_size) * tile_size
        y_cords = np.arange(0, h // tile_size) * tile_size
        x_grid, y_grid = np.meshgrid(x_cords, y_cords)
        tiles = np.column_stack((y_grid.ravel(), x_grid.ravel()))[:number_tiles]
        list_index.extend([img_name + str(tile) for tile in tiles])
        img_dict[img_name] = tiles
    return img_dict, list_index


def random_tile(input_folder, img_list, tile_size, number_tiles=None):
    if number_tiles is None:
        number_tiles = 1
    img_dict = {}
    list_index = []
    for img_name in tqdm(img_list, desc="Tile generation"):
        try:
            w, h = get_image_size(os.path.join(input_folder, img_name))
        except Exception:
            continue
        if w < tile_size or h < tile_size:
            continue
        x_cords = randint(0, w - tile_size - 1, number_tiles)
        y_cords = randint(0, h - tile_size - 1, number_tiles)
        tiles = np.column_stack((y_cords.ravel(), x_cords.ravel()))
        list_index.extend([img_name + str(tile) for tile in tiles])
        img_dict[img_name] = tiles
    return img_dict, list_index


def overlap_tile(input_folder, img_list, tile_size, number_tiles=None, overlap=0.25):
    if number_tiles is None:
        number_tiles = 10000
    img_dict = {}
    list_index = []
    for img_name in tqdm(img_list, desc="Tile generation"):
        try:
            w, h = get_image_size(os.path.join(input_folder, img_name))
        except Exception:
            continue
        if w < tile_size or h < tile_size:
            continue
        x_cords = np.arange(0, w // tile_size, overlap) * tile_size
        y_cords = np.arange(0, h // tile_size, overlap) * tile_size
        x_grid, y_grid = np.meshgrid(
            x_cords.astype(np.uint32), y_cords.astype(np.uint32)
        )
        tiles = np.column_stack((y_grid.ravel(), x_grid.ravel()))[:number_tiles]
        list_index.extend([img_name + str(tile) for tile in tiles])
        img_dict[img_name] = tiles
    return img_dict, list_index


TILE_FUNC = {"linear": lin_tile, "random": random_tile}


class Tiler:
    def __init__(self, config: dict):
        self.in_folder = config.get("in_folder")
        self.out_folder = config.get("out_folder")
        tiler = config.get("tiler")
        self.process_map = config.get("process", "thread")
        self.num_work = config.get("num_work")
        self.real_name = config.get("real_name")
        if self.out_folder is None:
            raise ValueError("You didn't include out_folder in config")
        elif self.in_folder is None:
            raise ValueError("You didn't include in_folder in config")
        elif tiler is None:
            raise ValueError("You didn't include tiler in config")
        if not os.path.exists(self.out_folder):
            os.makedirs(self.out_folder)
        self.img_list = [f for f in os.listdir(self.in_folder) if is_image_file(f)]
        self.tile_size = config.get("tile_size", 512)
        self.tiler_type = tiler.get("type", "linear")
        if self.tiler_type in ["linear", "random", "overlap"]:
            number_tiles = tiler.get("n_tiles")
            if self.tiler_type == "overlap":
                overlap = tiler.get("overlap", 0.25)
                self.img_dict, self.list_index = overlap_tile(
                    self.in_folder, self.img_list, self.tile_size, number_tiles, overlap
                )
            else:
                tile_func = TILE_FUNC[self.tiler_type]
                self.img_dict, self.list_index = tile_func(
                    self.in_folder, self.img_list, self.tile_size, number_tiles
                )
            self.img_list = list(self.img_dict.keys())
        else:
            raise ValueError("Unknown type")
        if config.get("shuffle"):
            shuffle(self.list_index)

    def __tile(self, origin_img, tile_cord):
        return origin_img[
            tile_cord[0] : tile_cord[0] + self.tile_size,
            tile_cord[1] : tile_cord[1] + self.tile_size,
        ]

    def __name(self, img_name, cord):
        if self.real_name:
            base_name = ".".join(img_name.split(".")[:-1])
            if cord is None:
                name = base_name + ".png"
            else:
                name = f"{base_name}_{cord[0]}_{cord[1]}.png"
        else:
            if cord is None:
                name = str(self.list_index.index(img_name)) + ".png"
            else:
                name = str(self.list_index.index(img_name + str(cord))) + ".png"
        return name

    def process(self, img_name):
        from dataset_forge.image_ops import Image
        from dataset_forge.image_ops import get_image_size
        from PIL import Image as PILImage

        img_path = os.path.join(self.in_folder, img_name)
        with PILImage.open(img_path) as img:
            img = img.convert("RGB")
            img = np.array(img)
        for tile_cord in self.img_dict[img_name]:
            out_name = self.__name(img_name, tile_cord)
            tile_img = self.__tile(img, tile_cord)
            out_path = os.path.join(self.out_folder, out_name)
            PILImage.fromarray(tile_img).save(out_path)

    def run(self):
        from tqdm.contrib.concurrent import process_map, thread_map

        if self.process_map == "thread":
            thread_map(
                self.process, self.img_list, max_workers=self.num_work, desc="Process"
            )
        elif self.process_map == "process":
            process_map(
                self.process, self.img_list, max_workers=self.num_work, desc="Process"
            )
        else:
            for img_name in tqdm(self.img_list, desc="Process"):
                self.process(img_name)


def tile_single_folder_grid(
    in_folder,
    out_folder,
    tile_size=512,
    process_type="thread",
    tiler_type="linear",
    n_tiles=None,
    overlap=0.25,
    shuffle=False,
    real_name=False,
    num_work=None,
    **kwargs,
):
    """
    Tiling for a single directory using grid-based logic (linear, random, overlap).
    """
    config = {
        "in_folder": in_folder,
        "out_folder": out_folder,
        "tiler": {
            "type": tiler_type,
            "n_tiles": n_tiles,
            "overlap": overlap,
        },
        "tile_size": tile_size,
        "shuffle": shuffle,
        "real_name": real_name,
        "process": process_type,
        "num_work": num_work,
    }
    tiler = Tiler(config)
    tiler.run()


def tile_hq_lq_dataset_grid(
    hq_folder,
    lq_folder,
    out_hq_folder,
    out_lq_folder,
    tile_size=512,
    process_type="thread",
    tiler_type="linear",
    n_tiles=None,
    overlap=0.25,
    shuffle=False,
    real_name=False,
    num_work=None,
    **kwargs,
):
    """
    Tiling for HQ/LQ paired directories using grid-based logic (linear, random, overlap).
    Only processes pairs where both HQ and LQ images exist, and applies the same tiling to both.
    """
    from PIL import Image as PILImage
    import numpy as np
    import os
    from tqdm import tqdm
    from dataset_forge.io_utils import is_image_file
    from dataset_forge.image_ops import get_image_size

    hq_files = set([f for f in os.listdir(hq_folder) if is_image_file(f)])
    lq_files = set([f for f in os.listdir(lq_folder) if is_image_file(f)])
    common_files = sorted(list(hq_files & lq_files))
    if not os.path.exists(out_hq_folder):
        os.makedirs(out_hq_folder)
    if not os.path.exists(out_lq_folder):
        os.makedirs(out_lq_folder)
    # Build tile coordinates for each image in HQ (and apply to LQ)
    if tiler_type == "overlap":
        img_dict, list_index = overlap_tile(
            hq_folder, common_files, tile_size, n_tiles, overlap
        )
    else:
        tile_func = TILE_FUNC[tiler_type]
        img_dict, list_index = tile_func(hq_folder, common_files, tile_size, n_tiles)
    if shuffle:
        np.random.shuffle(list_index)
    for img_name in tqdm(common_files, desc="Paired HQ/LQ Tiling"):
        hq_path = os.path.join(hq_folder, img_name)
        lq_path = os.path.join(lq_folder, img_name)
        with PILImage.open(hq_path) as hq_img:
            hq_img = hq_img.convert("RGB")
            hq_img = np.array(hq_img)
        with PILImage.open(lq_path) as lq_img:
            lq_img = lq_img.convert("RGB")
            lq_img = np.array(lq_img)
        for tile_cord in img_dict.get(img_name, []):
            # Use same naming logic as Tiler
            base_name = ".".join(img_name.split(".")[:-1])
            out_name = f"{base_name}_{tile_cord[0]}_{tile_cord[1]}.png"
            hq_tile = hq_img[
                tile_cord[0] : tile_cord[0] + tile_size,
                tile_cord[1] : tile_cord[1] + tile_size,
            ]
            lq_tile = lq_img[
                tile_cord[0] : tile_cord[0] + tile_size,
                tile_cord[1] : tile_cord[1] + tile_size,
            ]
            PILImage.fromarray(hq_tile).save(os.path.join(out_hq_folder, out_name))
            PILImage.fromarray(lq_tile).save(os.path.join(out_lq_folder, out_name))
