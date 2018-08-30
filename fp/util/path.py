import os

def files_in_dir(directory, exts=['.png']):
    '''returns filenames with exts in directory.'''
    if isinstance(exts, str):
        exts = [exts]
    return [f for f in os.listdir(directory) if 
            os.path.splitext(f)[1] in exts]