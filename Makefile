SKILL_NAME = anki
ZIP_FILE   = $(SKILL_NAME).zip

.PHONY: zip clean test

zip: clean
	mkdir -p build/$(SKILL_NAME)
	cp SKILL.md build/$(SKILL_NAME)/
	cp -r references scripts build/$(SKILL_NAME)/
	cd build && zip -r ../$(ZIP_FILE) $(SKILL_NAME) -x "*/__pycache__/*" -x "*/.DS_Store"
	rm -rf build
	@echo "✓ Created $(ZIP_FILE)"

test:
	python3 -m unittest discover -s tests -v

clean:
	rm -f $(ZIP_FILE)
	rm -rf build
