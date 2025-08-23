"""
fileprinter.py

A module for printing content inside a file with timing.
"""

import time


class FilePrinter:
    class create:
        def printfilecontent(self,filename, extension, path, focus):
            """
            Prints the content of a specified file.

            Parameters:
            - filename: name of the file (without extension)
            - extension: file extension (e.g., ".txt")
            - path: full path to file
            - focus: "filename" to open via filename + extension,
                     "path" to open via path
            """

            start_time = time.perf_counter()
            fileopen = False

            try:
                if focus == "filename":
                    f = open(filename + extension, "r")
                elif focus == "path":
                    f = open(path, "r")
                else:
                    print("Invalid focus parameter. Use 'filename' or 'path'.")
                    return
                fileopen = True

            except FileNotFoundError:
                elapsed = (time.perf_counter() - start_time) * 1000
                if focus == "filename":
                    print("File not found: " + filename + extension)
                elif focus == "path":
                    print("File in path not found: " + path)
                print(f"Process exited. Time elapsed: {elapsed:.2f} ms")

            except Exception as err:
                elapsed = (time.perf_counter() - start_time) * 1000
                print("Error:", err)
                print(f"Process exited. Time elapsed: {elapsed:.2f} ms")

            else:
                for line in f.readlines():
                    print(line, end="")  # avoid double newlines
                elapsed = (time.perf_counter() - start_time) * 1000
                print(f"\nProcess successful. Time elapsed: {elapsed:.2f} ms")

            finally:
                if fileopen:
                    f.close()
