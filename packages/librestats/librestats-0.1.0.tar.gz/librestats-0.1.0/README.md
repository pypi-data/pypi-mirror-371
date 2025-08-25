<p align="center">
  <img width="354" height="76" alt="librestats_py_logo" src="https://github.com/user-attachments/assets/35855611-e368-4969-b400-f32be5f25d2f" />
</p>

![GitHub forks](https://img.shields.io/github/forks/librestats/librestats-py?style=plastic&color=blue)
![GitHub License](https://img.shields.io/github/license/librestats/librestats-py?style=plastic)
![GitHub Repo stars](https://img.shields.io/github/stars/librestats/librestats-py?style=plastic&color=yellow)


# librestats

A Python library for accessing open and community-curated datasets enabling data scientists, researchers and students to load, analyze and visualize reliable data in just a few lines of code.

## Installation
```bash
pip install librestats
```

## Quick Start
```python
import librestats as ls

# 1. List available domains
print(ls.list_domains())  
# ➝ ['awards', 'economy', 'sports']

# 2. List datasets inside a domain
print(ls.list_datasets("awards"))  
# ➝ ['fields_medal_winners_data', 'nobel_prize']

# 3. Load a dataset in a DataFrame (df)
df = ls.load_dataset("awards", "fields_medal_winners_data")

# 4. Access data from a DataFrame (df)
ls.get(df,"Belgium","1978")
```

## Dataset Organization
Datasets are stored in structured domains making it easy to browse, extend and contribute!
```bash
datasets/
├── awards/
│   ├── fields_medal.csv
│   ├── nobel_prize.csv
|   ...
├── economy/
│   ├── gdp.csv
│   ├── inflation.csv
|   ...
├── sports/
│   ├── olympics.csv
│   ├── world_cup.csv
|   ...
...
```

With LibreStats, open data becomes more accessible, powerful and fun!<br>
We welcome dataset contributions and feature ideas!


