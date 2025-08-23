import os, itertools
from pathlib import Path

video_extensions = \
"""webm mkv flv flv vob ogv  ogg drc gif gifv mng avi mov 
qt wmv yuv rm rmvb viv asf  mp4  m4p m4v mpg  mp2  mpeg  mpe 
mpv mpg  mpeg  m2v m4v svi 3gp 3g2 mxf roq nsv""".split() # from wikipedia

def is_video(f):
    # True if name as video extension
    name_ext = f.split('.')
    if len(name_ext) != 2:
        return False
    name, ext = name_ext
    return ext.lower() in video_extensions

def find_ISO_vids_pairs(top):
    # top is 
    vids = []
    ISOs = []
    for (root,dirs,files) in os.walk(top, topdown=True):
        for d in dirs:
            if d[-4:] == '_ISO':
                ISOs.append(Path(root)/d)
        for f in files:
            if is_video(f):
                vids.append(Path(root)/f)        
    matches = []
    for pair in list(itertools.product(vids, ISOs)):
        # print(pair)
        vid, ISO = pair
        vidname, ext = vid.name.split('.')
        if vidname == ISO.name[:-4]:
            matches.append(pair)
        # print(vidname, ISO.name[:-4])
    return matches

[print( vid, ISO) for vid, ISO in find_ISO_vids_pairs('.')]
