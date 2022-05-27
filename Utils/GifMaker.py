import glob
from PIL import Image

def get_theta_multiple(path):
    return int(path.split("=")[-1].split("over")[0])

def make_gif(stills_path, output_path, duration = None):
    paths = [im for im in glob.glob(f"{stills_path}/*.png")]
    paths.sort(key=lambda x: get_theta_multiple(x))
    if not duration:
        duration = len(paths)*30
    frames = [Image.open(image) for image in paths]
    frame_one = frames[0]
    frame_one.save(output_path, format="GIF", append_images=frames,
               save_all=True, duration=duration, loop=0)