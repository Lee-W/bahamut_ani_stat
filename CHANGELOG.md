# Changelog
## 0.9.0 (2025-05-07)

### Feat

- **cruft**: update dep tool as uv and python version to 3.12

## 0.8.1 (2024-08-13)

### Fix

- update deps with breaking changes and change the existing implementation accordingly

## 0.8.0 (2023-01-06)

### Feat

- **cli/db**: make retry_limit an option
- **cli/db**: add only-old-anime flag
- **cli/db**: add retry mechanism

### Fix

- **parser**: fix review count xpath

## 0.7.1 (2022-09-28)

### Fix

- **parser**: get next_request after receive 301 from ANIME_REF_URL

## 0.7.0 (2022-09-18)

### Feat

- update from cruft template

## 0.6.0 (2022-05-19)

### Feat

- **db_commands**: set sleep upper bound to 10 and lower boung to 0

## 0.5.0 (2022-05-19)

### Feat

- **db_command**: add random sleep flag

## 0.4.1 (2022-01-26)

### Fix

- **plot**: remove five point system start date from x axis start point

## 0.4.0 (2021-10-21)

### Feat

- **model**: remove anime_feature and replace it with star_percentage from 1 ~ 5
- **cli/plot**: add score axis range

### Refactor

- **config**: use pydantic to manage settings

### Fix

- **parser**: update score parsing as bahamut recently replaces 10 point system with 5 point system
- **cli/db**: use is_avaiable isnot(False) to filter out available animes

## 0.3.3 (2021-10-01)

### Fix

- **cli/db**: fix update anime is_available

## 0.3.2 (2021-09-26)

### Fix

- **parser**: fix "parse get-new-animes --print-output" command

## 0.3.1 (2021-09-26)

### Refactor

- **parser**: replace dataclass with pydantic for data_types in parser module

## 0.3.0 (2021-09-04)

### Fix

- **parser**: handle 沒有此部作品 message
- handle unaviable anime cases
- **cli/db**: remove 電影 from new anime
- **plot**: filter wrongly filter out view counts
- **plot**: handle anime score and anime view count not exist exception
- **plot**: remove tmp fix for view count parsing error
- **db/model**: fix anime score table definition
- **parser**: fix view count regular expression

### Feat

- **db-cli**: skip detail parsing if the anime is no longer available
- **cli**: add cli description
- **db**: add studio, agent, director tables
- **plot**: rename new-anime-trend as anime-trend and add filter
- **plot**: combine score into new anime trend
- **plot**: add new anime view count trend
- **plot**: add hover tool to plot premium
- **plot**: add link back to bahamut through sn
- **parser**: add labels to animes
- **plot**: add widgets to anime plot
- **plot**: add latest anime score to plot anime command
- **cli/db**: add add_animes_detail command
- **cli**: add message to db and plot commands
- **cli/plot**: add plot anime command
- **cli/plot**: add plot premium rate command
- **cli/db_commands**: implement add-animes-base-data, add-new-animes
- **model**: add is_new column to Anime table
- **cli**: refactor commands into parse_command group and add db_command_group
- **parser**: add arguments to_dict and ignore_none for parser methods
- **db**: initial db models
- **cli**: add get_new_animes_command
- **cli**: add get_premium_rate_command

### Refactor

- **plot**: refactor query sql
- unify hover tool datetime format
- **plot**: update hover tool label
- **plot**: abstract _group_stat from plot new anime trend
- rename functions
- **parser**: rename column name in data_types and make parser returns only data with types defined
- **parser**: rename get_*_base_animes_* as get_*_animes_base_*

## 0.2.0 (2021-07-05)

### Feat

- **parser**: use lxml as bs4 parser
- **parse**: implement method to parse ani gamer statistics and anime intro

## 0.1.0 (2021-07-05)

### Feat

- project initialization
