# Narrator Identity and Delivery

The default is the user-approved “Steady Male Voice — Tight Phrasing and Clear Emphasis.” The [reference audio](../assets/voice/reference.wav) preserves the complete 14.72-second audition. Use its voice character, narrative rhythm, and emphasis as a listening reference. See the [Voice Profile](../assets/voice/profile.json) for its source, transcript, generation settings, and approval status.

Synthesis uses the same Qwen3-TTS CustomVoice 1.7B 8bit model, Ryan preset, and model revision as the audition. reference.wav is a listening reference, not an input to the Base model for recloning. Replacing the WAV alone does not change CustomVoice's preset identity. If the user selects another voice, keep the reference file, profile, model lock, and actual invocation consistent.

Production remains Chinese, using zh-CN. Maintain a mature, full, resonant male voice with tight, natural conversational phrasing. Preserve the model's native voice character without automatically lowering the pitch, reshaping resonance, boosting bass, or retiming the audio.

## Let the script shape the delivery

The voice stays consistent; each passage's delivery changes. Keep thought groups connected, move lightly through secondary words, and give key words brief, decisive emphasis. Use short pauses between ordinary sentences and more space at turns and conclusions. A steady delivery need not be slow, and emphasis need not mean shouting or stretching vowels. Adjust to the argument, emotion, and human situation rather than giving every sentence the same speed, stress, and tone.

segments[].direction specifies how this passage should be read. The script places it between the profile's general delivery instructions and passes the result to the model as instruct. For example, in “更重要的是” (“more importantly”), stress “更重要” and move naturally through “的是.” Emphasis must follow the current passage rather than recycle words from the reference script. The model's ability to accept instructions does not guarantee faithful execution; listen to the result.

Use the [Performance Plan Template](../assets/voice/performance-template.json) to write the project's voice-plan.json, replacing its example content. Keep the final script in text. Use tts_text only for necessary pronunciation corrections, while captions retain the correct written form. Record the take's seed in the plan. gap_after represents only additional space genuinely needed at that point in the thought.

## Synthesis and listening review

Generate complete thought groups or paragraphs to preserve emotional continuity and context. Do not generate a few words separately for every emphasis and splice them together. If the reading sounds flat, revise direction, phrasing, and emphasis first. If it drags, adjust the native generation instructions rather than speeding up playback or compressing every pause. The reference's 14.72 seconds describes that sample only; it does not set the duration of other scripts.

Keep context in pickups and check voice continuity and intact beginnings and endings. Regenerate a take that reaches the token limit, or split it at a natural turn in meaning. Do not trim away the ending to solve a duration problem. Check missing words, repetitions, ambiguous pronunciations, names, drawn-out sounds, mechanical pauses, and changes in voice character. ASR helps locate text problems; it cannot certify naturalness, emphasis, or emotion.

generation.json records the actual model, speaker, reference checksum, each segment's instruct and seed, and sampling settings to help identify changes in delivery. Review every new script by listening; approval of the default reference does not automatically pass a new reading.

When execution is needed, follow [Runtime Setup](runtime.md). If the user only requests Skill changes, update files and invocation settings without also generating narration, installing environments, or running a trial for them.
