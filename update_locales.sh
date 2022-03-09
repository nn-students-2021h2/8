# Step 1:
pybabel extract --input-dirs=. -o locales/bot.pot
pybabel update -d locales -D bot -i locales/bot.pot

# Step 2: update the translations in bot.po files (it should be done manually)

# Step 3: compile the translationed files
pybabel compile -d locales -D bot