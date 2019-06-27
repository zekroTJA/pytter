#!/bin/bash

rm -r docs/*

pdoc \
    --html \
    --html-dir docs \
    --overwrite \
    --external-links \
        pytter

mv docs/pytter/* docs/

rm -r docs/pytter