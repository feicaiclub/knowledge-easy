# Rebuilding the component previews

The visual handbook includes still previews in both languages. Pre-rendered demo videos are not bundled. Raw third-party source clips are not redistributed with the open-source package.

To rebuild the catalog, provide a folder of footage you are licensed to use:

```sh
sh "<skill>/scripts/run.sh" catalog --project "<new-demo-project>" --language en-US --media-dir "<licensed-clips>"
```

The nine-variant catalog uses `street.mp4`, `blue.mp4`, `book.mp4`, `chess.mp4`, and `notes.mp4`. The twelve base designs (`--base`) also use `clock.mp4`, `portrait.mp4`, `rain.mp4`, and `typing.mp4`. Use clips at least 12 seconds long. These filenames identify editable sample slots, not required stock titles. The command reports any missing files before creating a project.

For a new film, use `init` and choose footage for the story. You do not need these catalog clips. Recorded research sources are in [the asset guide](../../../references/assets.md).
