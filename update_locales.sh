# Step 1: extract all the marked string from the code and update bot.po files in locales/*lang*/LC_MESSAGES folder
pybabel extract --project=FunctionExplorerBot --version=1.1 --keywords=__ --input-dirs=. -o locales/bot.pot
pybabel update -d locales -D bot --update-header-comment -N -i locales/bot.pot

# Step 2: update the translations in bot.po files (it should be done manually! To update russian translations,
# open locales/ru/LC_MESSAGES/bot.po file and find not translated lines)

# Step 3: compile the translated files
pybabel compile -d locales -D bot
