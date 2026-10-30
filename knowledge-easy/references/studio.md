# Reviewing in Lazy Studio

When the user wants to review a film, register an existing export first, using a distinct ID and filename for each version. The launcher binds to local address 127.0.0.1. If another project occupies the port, choose a different port rather than terminating an unrelated process.

Space plays or pauses. The arrow keys step through frames. Press M to mark the current frame, write a comment, then press Enter to save the text and screenshot. Shift + Enter inserts a line break. Keep two versions side by side for comparison.

The complete event history remains in review/feedback.jsonl, with screenshots in review/frames/. Each version has its own generated review/versions/<id>/feedback.md and feedback.jsonl views; these are the files linked in the sidebar. The project-level review/feedback.md remains available for compatibility. Older projects retain their own feedback paths; use the paths returned by the interface. Comments can be edited, deleted, copied, and used to jump back to their original frames. The sidebar, counts, copy action, and review notes follow the selected A version. Resolved marks retain their update notes; removed marks appear in a collapsed history section for that version and are not pending edits.

Attach version-specific review notes with `register --review-file <notes.md>`; the path is relative to the project. Existing projects can map revision IDs to note files in studio.json under self_reviews. A new version does not inherit another version's review document.

When the user returns to the original conversation and says the feedback is ready, read the files and screenshots and revise the specified versions and frames without asking them to repeat their notes. Preserve existing feedback and register each new export separately.

This interface reviews existing videos. Editing the Skill does not automatically start the review server or generate a new film.
