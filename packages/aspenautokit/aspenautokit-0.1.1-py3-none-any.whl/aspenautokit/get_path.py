# aspenautokit/get_path.py
import os
import aspenautokit

# This will get the path to the directory where your package is installed
# (e.g., C:\Python39\Lib\site-packages\aspenautokit)
package_path = os.path.dirname(aspenautokit.__file__)
print(package_path)