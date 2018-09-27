import os

def files_in_dir(directory, exts=['.png'], include_dir=False):
    '''returns filenames with exts in directory.'''
    if isinstance(exts, str):
        exts = [exts]
    if include_dir:
        return [os.path.join(directory, f) for f in os.listdir(directory)
                if os.path.splitext(f)[1] in exts]
    else:
        return [f for f in os.listdir(directory) if
                os.path.splitext(f)[1] in exts]