## resets folder structures when using gui curator

import os
import shutil
from pathlib import Path

def clear_directories(directories):
    keepfile="logo.png"
    # for directory in directories:
    #     try:
    #         for root, dirs, files in os.walk(directory):
    #             for file in files:
    #                 file_path = os.path.join(root, file)
    #                 os.remove(file_path)
    #             for dir in dirs:
    #                 shutil.rmtree(dir)
    #     except Exception as e:
    #         print(f"exception: {e}. {directory}")
    #         shutil.rmtree(directory)

    for directory in directories:
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file != keepfile:
                        os.remove(file_path)
                for dir in dirs:
                    if dir != "static":
                        dir_path = os.path.join(root, dir)
                        shutil.rmtree(dir_path)
        except Exception as e:
            print(f"exception: {e}. {directory}")
            shutil.rmtree(directory)

            
    templates_path = Path('./templates')
    html_files = list(templates_path.glob('*.html'))
    for file in html_files:
        filename = file.stem  # Get the filename without extension

        if filename == 'inspect_final':
            continue
        if filename.startswith('inspect'):
            try:
                index = int(filename[7:])  # Ignore the first 7 characters ('inspect')
                if index >-1:
                    os.remove(file)
                    print(f"removing {file}")
            except ValueError:
                print(f"Warning: File '{file.name}' does not have a proper integer index.") # If there is no integer after 'inspect', print a warning and continue

    static = Path("./static")
    static.mkdir(parents=True, exist_ok=True)

    try:
        shutil.copy("logo.png", "static")
    except:
        print("")


if __name__ == '__main__':
    directories = ['../static', '../example_review', '../included', '../recordings', '../slice_review']
    directories = ['./static', './example_review', './included', './recordings', './slice_review']

    clear_directories(directories)


    print(f"cleared directories {directories}")
    # static = Path("./static")
    # static.mkdir(parents=True, exist_ok=True)

    # shutil.copy("logo.png", "static")
    