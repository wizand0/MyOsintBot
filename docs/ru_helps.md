Option 1. Using the tree command in the terminal (Linux / macOS / WSL)

1. Installing the tree utility:  

   • Ubuntu/Debian:  
     ```
     sudo apt update && sudo apt install tree
     ```

2. Generating the project tree:  
   Navigate to the root folder of your project and run the command:
   ```
   tree -L 2 > README.md
   ```

   Here:

   • -L 2 limits the displayed depth to 2 levels (replace the number with another value if necessary);

   • > README.md saves the output to the file README.md. If README.md already exists, the command will overwrite its contents.

---

Below is one approach for automatically generating a similar project structure, including a list of methods (functions) within files, which can be inserted into the Readme.md file. The idea is to write a specialized Python script that:

1. Recursively traverses the folders and files of the project.

2. For each Python file, uses the ast module to parse its contents and extract the function definitions (and, if necessary, class methods).

3. Formats a textual visualization in the form of a "tree" that can be inserted into the Readme.md.

Below is an example of such a script.

---

▎How to Use

1. Place the script.  
   Save the script in a file—for example, generate_tree.py in the root of your project.

2. Run the script.  
   Execute the following command in the terminal:
   
   python generate_tree.py > structure.txt
   
   The file structure.txt will contain the generated project tree with the list of functions (you can immediately open this file, copy its contents, and paste them into Readme.md).

3. Editing.  
   A small modification may be necessary for your needs. For example, you can choose to output functions only from the top level or also those inside classes, adjust the tree formatting, etc.

---

▎Note

If there is a .gitignore file in the root directory, it will be used to exclude the files and folders that meet the specified rules. To parse .gitignore, it is convenient to use the pathspec package (https://pypi.org/project/pathspec/). You can install it by running:
pip install pathspec