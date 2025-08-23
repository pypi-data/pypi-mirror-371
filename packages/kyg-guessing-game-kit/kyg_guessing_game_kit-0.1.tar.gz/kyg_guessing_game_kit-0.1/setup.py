from setuptools import setup, find_packages

setup(
    name="kyg-guessing-game-kit",
    version="0.1",
    description="KYG: Guessing Game Kit – Playful Python Learning by Ashok Sir and Sathish Ramanujam",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Ashok Bakthavathsalam, Sathish Ramanujam",
    author_email="ashok@kgisl.com, sathishse13@gmail.com",
    url="https://www.ashokbakthavathsalam.com/",
    packages=find_packages(),
    install_requires=[],  # tkinter is standard but included
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "kyg-ggk=kyg_ggk.main:main"  # Your main function entry point, ensure main.py has def main()
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Education",
        "Topic :: Games/Entertainment",
        "Intended Audience :: Education",        
        "Natural Language :: English",
    ],
    keywords="python education game guessing tkinter induction zero2hero",
)
