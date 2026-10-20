// Audio manager — SILENT PLACEHOLDERS.
// TODO: add sound — no audio files ship with this repo and none may be
// downloaded; every entry below is a silent placeholder already wired to
// the right gameplay event. Drop real files under game/assets/audio/ and
// map them in SOUND_FILES to activate (names come from CONFIG.audio).
import { CONFIG } from './config.js';

const SOUND_FILES = {
  // player_shoot: 'assets/audio/player_shoot.ogg',     // TODO: add sound
  // player_hit: 'assets/audio/player_hit.ogg',         // TODO: add sound
  // player_death: 'assets/audio/player_death.ogg',     // TODO: add sound
  // enemy_hit: 'assets/audio/enemy_hit.ogg',           // TODO: add sound
  // enemy_explosion: 'assets/audio/enemy_explosion.ogg', // TODO: add sound
  // powerup_collect: 'assets/audio/powerup_collect.ogg', // TODO: add sound
  // bomb_use: 'assets/audio/bomb_use.ogg',             // TODO: add sound
  // boss_warning: 'assets/audio/boss_warning.ogg',     // TODO: add sound
  // boss_growl: 'assets/audio/boss_growl.ogg',         // TODO: add sound
  // boss_hit: 'assets/audio/boss_hit.ogg',             // TODO: add sound
  // boss_death: 'assets/audio/boss_death.ogg',         // TODO: add sound
  // ui_click: 'assets/audio/ui_click.ogg',             // TODO: add sound
  // ui_pause: 'assets/audio/ui_pause.ogg',             // TODO: add sound
  // music_stage: 'assets/audio/music_stage.ogg',       // TODO: add sound
  // music_boss: 'assets/audio/music_boss.ogg',         // TODO: add sound
};

export class AudioManager {
  constructor() {
    this.volume = CONFIG.audio.masterVolume;
    this.currentMusic = null;
    this.muted = false;
  }

  play(name) {
    if (this.muted) return;
    const file = SOUND_FILES[name];
    if (!file) return; // TODO: add sound (silent placeholder)
    // new Audio(file).play() would go here once files exist.
  }

  setMusic(name) {
    if (this.currentMusic === name) return;
    this.currentMusic = name;
    // TODO: add sound — music_stage / music_boss are silent placeholders.
  }
}
