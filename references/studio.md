# Reviewing in Lazy Studio

Register an existing export before opening the local review room. Give each revision a new ID and filename.

```sh
sh "<skill>/scripts/run.sh" register --project "<project>" --file final/film-v1.mp4 --label "First cut" --id v1
sh "<skill>/scripts/run.sh" studio --project "<project>" --port 8798
```

The launcher prepares the required media tools and binds the server to `127.0.0.1`. Check that the returned URL works, then open it in the available in-app browser. If the port belongs to another project, choose a different port; do not stop an unrelated process.

Press Space to play, Left or Right to step one frame, and M to mark a frame. Write a comment and press Enter to save it with a screenshot. Shift+Enter inserts a line break. Comparison stays side by side. The sidebar has only Marks and Review, with no separate chat or model runner.

New projects save feedback in `review/feedback.md`, images in `review/frames/`, and exact version/frame records in `review/feedback.jsonl`. Older projects keep their existing feedback filename; use the path returned by `/api/project`. Comments can be edited, removed, copied, and used to jump back to the original frame. Unicode comments work in either film language.

The Review tab shows a real project review document, such as `final/review.md`, or the configured file. Missing review notes are not evidence of a completed review.

Saving locally does not attach anything to the chat composer. When the user returns to the original chat and says feedback is ready, read the saved file and screenshots. Do not ask them to retype comments. Match each comment to its original revision and frame, then register the new export for comparison. Keep existing feedback intact.

The interface and server are bundled. Claude Code and a separate Codex runner are not required.
