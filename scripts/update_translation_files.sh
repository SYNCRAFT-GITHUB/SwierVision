#!/bin/sh

# Update pot
xgettext --keyword=_ --keyword=ngettext:1,2 --language=Python --no-location --sort-output \
    -o sv_includes/locales/SwierVision.pot \
    *.py \
    sv_includes/*.py \
    panels/*.py \
    sv_includes/defaults.conf
# Update po
for FILE in sv_includes/locales/*; do
    if [ -d $FILE ]; then
        echo Processing $FILE
        msgmerge -q $FILE/LC_MESSAGES/SwierVision.po \
                 sv_includes/locales/SwierVision.pot \
              -o $FILE/LC_MESSAGES/SwierVision.po
        # Clean Fuzzy translations
        msgattrib --clear-fuzzy --empty -o $FILE/LC_MESSAGES/SwierVision.po $FILE/LC_MESSAGES/SwierVision.po
        # Compile mo
        msgfmt -o  $FILE/LC_MESSAGES/SwierVision.mo $FILE/LC_MESSAGES/SwierVision.po
    fi
done
