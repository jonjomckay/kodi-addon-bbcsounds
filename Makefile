addon_xml := addon.xml
include_files = addon.py addon.xml LICENSE README.md resources/
include_paths = $(patsubst %,$(name)/%,$(include_files))

name = $(shell xmllint --xpath 'string(/addon/@id)' $(addon_xml))
version = $(shell xmllint --xpath 'string(/addon/@version)' $(addon_xml))

zip:
	@rm -f $(name)
	@ln -s . $(name)
	zip -r $(name)-$(version).zip $(include_paths)
	@rm -f $(name)
