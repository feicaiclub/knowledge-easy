# English and Chinese production

The Skill, documentation, and review interface are written in American English. The film's language is a separate setting: `en-US` or `zh-CN`. English is the default for new projects. Existing projects without a language field retain the earlier Chinese behavior.

```sh
sh "<skill>/scripts/run.sh" init --project "<project>" --language en-US
sh "<skill>/scripts/run.sh" catalog --project "<new-demo-project>" --language en-US
```

Set `project.json`, `film.json`, and `voice-plan.json` to the same language. The tools reject conflicting settings. Use `zh-CN` for Chinese narration and layouts; no second Skill is required.

## English writing and narration

Write for spoken American English: clear verbs, natural contractions, varied sentence lengths, and concrete examples. Rebuild awkward literal translations around their meaning. Keep the evidence, intended argument, and emotional progression intact. Do not introduce new claims while adapting the script.

The voice command selects English synthesis, and transcription selects English recognition. The speaker reference remains the approved D voice. Its transcript stays in Mandarin because it must describe the actual reference recording; translating that transcript would make the audio/text pair incorrect. The user approved the bundled English pilot's accent and naturalness; its exact hash is recorded in the voice profile. Review pronunciation, pacing, and speaker consistency on each new take. Do not infer listening approval from the language setting or a successful transcript.

Keep spelling in the script and captions correct. Put pronunciation changes only in a segment's `tts_text` or the episode's pronunciation notes. Check names, acronyms, dates, currencies, abbreviations, and quoted languages. English sample entries live in `assets/voice/pronunciations.en-US.json`; Chinese entries remain available separately.

## English typography and captions

Use Source Serif 4 for English display text, Inter for explanations and captions, and Barlow Condensed for numbers. Chinese uses the existing Noto Serif SC and Noto Sans SC families. Fonts and their licenses are bundled.

English phrases usually need different line breaks from Chinese. Break at phrase boundaries and keep words together. Avoid a one-word last line, stranded punctuation, all-caps paragraphs, and tiny type used to force a sentence into a card. Shorten or restructure the copy when it does not fit. Review names, connectors, map labels, and subtitles in the actual export.

Use English place names or established romanizations in an English film. Confirm dates, units, number formatting, and labels for the audience; do not change measurement systems or historical names without checking the meaning. Keep map projection and factual geometry independent of label language.

Caption timing comes from the English recording, not the Chinese version. Keep captions to two readable lines and split them at natural phrase boundaries. Word timestamps are a starting point, not a reading-quality verdict.

## Review

Check script language, TTS language, ASR language, captions, graphic labels, and typography together. Listen for unexpected language switching, a noticeable accent mismatch, names read incorrectly, and speaker drift. Watch for English text spilling out of a layout or revealing information before the narration reaches it. Chinese examples and the Mandarin reference transcript are intentional bilingual assets, not untranslated interface text.
