from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Terminal-Speil-B1",
    version="1.1.0",
    author="Basanta Bhandari",
    author_email="bhandari.basanta.47@gmail.com",
    description="A terminal-based spelling game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/basanta-bhandari/Summer_of_Making",
    py_modules=["Terminal_Speil_Main", "utils", "game_data", "save_system"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment :: Role-Playing",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "terminal-speil-b1=Terminal_Speil_Main:main",
        ],
    },
)