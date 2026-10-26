# Series voice and episode delivery

The default narrator is the approved D voice. Each synthesis uses `assets/voice/reference.wav` and `profile.json`, then applies `timbre-body-v1.json`. The reference file's SHA256 is checked before generation; an unexpected change stops the run.

The reference recording, pinned model, and finishing settings maintain the voice identity. `voice_design_seed` records how the reference was originally designed; a new episode does not redesign the voice from that seed. A segment's `seed` controls sampling, not speaker identity. Neither a seed nor a file hash can guarantee that generated speech never drifts.

Set the project and voice plan to `en-US` or `zh-CN`. English text uses English synthesis with the same reference. Keep the reference transcript exactly as recorded, even when the new film is in English. Check accent and pronunciation in an English pilot rather than assuming the language flag guarantees an American delivery.

Body-v1 lowers pitch slightly and adds low-mid body while preserving playback speed, sample count, and pauses. Processing uses existing quiet regions with context on each side. It does not trim the first or last syllable.

Calibrate performance on a representative passage before expanding to the full film. Keep identity, pace, phrasing, pitch and emotional emphasis as separate judgments. If a take feels flat, first examine the intended stress, sentence connection and pauses; raising pitch or applying a large speed change is not a substitute. If the user supplies a voice or names another provider, keep that identity and its actual controls in the project instead of changing the global default reference.

Design delivery for the subject. Decide which ideas belong together, where an event ends, where reflection begins, and which words carry weight. `direction` records that intent; the Base model does not provide a reliable emotional instruction parameter. Use wording, punctuation, complete passages, and take selection rather than pretending an unsupported parameter controls the performance.

```json
{
  "language": "en-US",
  "segments": [{
    "id": "opening",
    "text": "Knowing what happened is only the beginning. The harder question is why it made sense to the people who were there.",
    "direction": "Start conversationally. Give the second sentence weight without slowing every word.",
    "seed": 22102271,
    "max_tokens": 3500,
    "gap_after": 0
  }]
}
```

Generate complete passages, not isolated sentences. Include surrounding context when replacing a take. Use the same reference for the ending. Reject a take that hits its token limit; raise the limit or divide the text at a meaningful narrative break. Never solve a length problem by clipping speech.

`tts_text`, when supplied, changes only the text sent to TTS; the script and captions keep their original spelling. Pronunciation files are review aids, not blind global replacements. Check omissions, repetitions, names, pauses, the first and last syllables, and voice identity throughout. ASR helps find textual errors but does not certify tone, accent, or naturalness. State clearly when listening has not been performed.

Start with the approved MLX implementation, model revision, reference, and body-v1 settings. If that setup cannot run on the user's machine, follow the [runtime adaptation guidance](runtime.md). Prefer a compatible implementation that can use the same model and reference, explain any tradeoffs, and check a short take against the approved voice. Installing successfully is not voice-quality approval.

The user listened to and approved the [English pilot](../assets/voice/english-pilot.wav) on October 22, 2026, explicitly confirming that file. The exact sample and its SHA256 are recorded in the voice profile. It uses the same reference and finishing profile; it is not a replacement reference. This approves the pilot's delivery, not every future take.
