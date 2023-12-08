#!/bin/sh

# Update pot
xgettext --keyword=_ --keyword=ngettext:1,2 --language=Python --no-location --sort-output \
    -o ks_includes/locales/IDEXScreen.pot \
    *.py \
    ks_includes/*.py \
    panels/*.py \
    ks_includes/defaults.conf
# Update po
for FILE in ks_includes/locales/*; do
    if [ -d $FILE ]; then
        echo Processing $FILE
        msgmerge -q $FILE/LC_MESSAGES/IDEXScreen.po \
                 ks_includes/locales/IDEXScreen.pot \
              -o $FILE/LC_MESSAGES/IDEXScreen.po
        # Clean Fuzzy translations
        msgattrib --clear-fuzzy --empty -o $FILE/LC_MESSAGES/IDEXScreen.po $FILE/LC_MESSAGES/IDEXScreen.po
        # Compile mo
        msgfmt -o  $FILE/LC_MESSAGES/IDEXScreen.mo $FILE/LC_MESSAGES/IDEXScreen.po
    fi
done
