const TICKS_PER_SECOND = 480;
const MICROSECONDS_PER_QUARTER = 1000000;
const CHANNEL_BY_ROLE = {
  melody: 0,
  chord: 1,
  bass: 2,
};
const PROGRAM_BY_ROLE = {
  melody: 0,
  chord: 24,
  bass: 32,
};

const textEncoder = new TextEncoder();

const toBytes = (value, byteCount) => {
  const bytes = [];
  for (let shift = (byteCount - 1) * 8; shift >= 0; shift -= 8) {
    bytes.push((value >> shift) & 0xff);
  }
  return bytes;
};

const encodeVariableLength = (value) => {
  let buffer = value & 0x7f;
  const bytes = [];

  while ((value >>= 7)) {
    buffer <<= 8;
    buffer |= (value & 0x7f) | 0x80;
  }

  while (true) {
    bytes.push(buffer & 0xff);
    if (buffer & 0x80) {
      buffer >>= 8;
    } else {
      break;
    }
  }

  return bytes;
};

const pushText = (target, text) => {
  target.push(...textEncoder.encode(text));
};

const secondsToTicks = (seconds) => Math.round(Number(seconds) * TICKS_PER_SECOND);

export function createMidiBlobFromMelody(melody) {
  const events = [
    { tick: 0, order: 0, bytes: [0xff, 0x51, 0x03, ...toBytes(MICROSECONDS_PER_QUARTER, 3)] },
  ];

  Object.entries(CHANNEL_BY_ROLE).forEach(([role, channel], index) => {
    events.push({ tick: 0, order: index + 1, bytes: [0xc0 + channel, PROGRAM_BY_ROLE[role]] });
  });

  melody.forEach((note, index) => {
    const channel = CHANNEL_BY_ROLE[note.role] ?? 0;
    const startTick = secondsToTicks(note.startTime);
    const endTick = secondsToTicks(note.startTime + note.duration);
    const pitch = Math.round(Math.min(127, Math.max(0, note.pitch)));
    const velocity = Math.round(Math.min(127, Math.max(1, note.velocity)));

    events.push({ tick: startTick, order: 10 + index * 2, bytes: [0x90 + channel, pitch, velocity] });
    events.push({ tick: endTick, order: 11 + index * 2, bytes: [0x80 + channel, pitch, 0x00] });
  });

  events.sort((a, b) => a.tick - b.tick || a.order - b.order);

  const track = [];
  let previousTick = 0;
  events.forEach((event) => {
    track.push(...encodeVariableLength(event.tick - previousTick), ...event.bytes);
    previousTick = event.tick;
  });
  track.push(0x00, 0xff, 0x2f, 0x00);

  const bytes = [];
  pushText(bytes, "MThd");
  bytes.push(...toBytes(6, 4), ...toBytes(0, 2), ...toBytes(1, 2), ...toBytes(TICKS_PER_SECOND, 2));
  pushText(bytes, "MTrk");
  bytes.push(...toBytes(track.length, 4), ...track);

  return new Blob([new Uint8Array(bytes)], { type: "audio/midi" });
}

export function exportMidi(melody) {
  if (!melody?.length) return;

  const url = URL.createObjectURL(createMidiBlobFromMelody(melody));
  const link = document.createElement("a");
  link.href = url;
  link.download = "echoes-soundscape.mid";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
