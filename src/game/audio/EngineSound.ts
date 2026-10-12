/**
 * EngineSound.ts - Web Audio API Synthesizer for high-performance race cars
 * Procedurally generates a balanced 50/50 hybrid acoustic profile:
 * - Deep, heavy, guttural American Racing V8 muscle roar (cross-plane firing order, 35-360 Hz)
 * - Subtle, progressive, high-tech F1 hybrid turbo / MGU-K whine (silky sine wave, 1.5-3.4 kHz)
 * - Pure zero-backfire acoustics: no pops, bangs, or artificial detonations.
 */

export class EngineSound {
  private ctx: AudioContext | null = null;
  private isMuted: boolean = false;
  private isInitialized: boolean = false;

  // Continuous anti-jitter DSP phase smoothing state
  private smoothBaseFreq: number = 37.5;
  private smoothRpmNorm: number = 0;
  private smoothThrottleNorm: number = 0;

  // Branch A: American Muscle Competition V8 Synthesizer (Heavy Low-Mid Core & High-Pressure Exhaust)
  private oscBase: OscillatorNode | null = null;
  private oscHarmonic1: OscillatorNode | null = null;
  private oscHarmonic2: OscillatorNode | null = null;
  private oscIntake: OscillatorNode | null = null;
  private oscSub: OscillatorNode | null = null;
  private combustionWave: PeriodicWave | null = null;
  private collectorWave: PeriodicWave | null = null;
  private gainBase: GainNode | null = null;
  private gainH1: GainNode | null = null;
  private gainH2: GainNode | null = null;
  private gainIntake: GainNode | null = null;
  private gainSub: GainNode | null = null;
  private intakeFilter: BiquadFilterNode | null = null;
  private exhaustResonance: BiquadFilterNode | null = null;
  private exhaustBassPunch: BiquadFilterNode | null = null;
  private revLimiterGain: GainNode | null = null;
  private isAtLimiterActive: boolean = false;
  private nextLimiterTime: number = 0;
  private limiterBarkBuffer: AudioBuffer | null = null;
  private engineBusGain: GainNode | null = null;
  private compressor: DynamicsCompressorNode | null = null;
  private masterGain: GainNode | null = null;
  private engineFilter: BiquadFilterNode | null = null;
  private distortion: WaveShaperNode | null = null;
  private distortionPreGain: GainNode | null = null;
  private distortionPostGain: GainNode | null = null;

  // Branch B: Subtle High-Tech F1 Hybrid Aero / MGU-K Whine Synthesizer (50/50 Balance)
  private f1WhineOsc: OscillatorNode | null = null;
  private f1WhineFilter: BiquadFilterNode | null = null;
  private f1WhineGain: GainNode | null = null;

  // Turbo whistle
  private turboOsc: OscillatorNode | null = null;
  private turboGain: GainNode | null = null;

  // Screech & rumble state tracking to prevent redundant AudioParam rescheduling
  private currentScreechGain: number = 0;
  private currentRumbleGain: number = 0;

  // Straight-Cut Gearbox Whine & Tarmac Hum
  private gearWhineOsc: OscillatorNode | null = null;
  private gearWhineGain: GainNode | null = null;

  // 3-Band Acoustic Tire Screech & Granular Rubber Friction
  private screechGain: GainNode | null = null;
  private screechFilter: BiquadFilterNode | null = null;
  private screechNoiseBuffer: AudioBuffer | null = null;
  private screechSource: AudioBufferSourceNode | null = null;
  private tireRumbleGain: GainNode | null = null;
  private tireRumbleFilter: BiquadFilterNode | null = null;
  private tireTearGain: GainNode | null = null;
  private tireTearFilter: BiquadFilterNode | null = null;

  // Granular metal barrier scraping & spark crackle synthesizer
  private scrapeGain: GainNode | null = null;
  private scrapeFilter: BiquadFilterNode | null = null;
  private scrapeCrackleGain: GainNode | null = null;
  private scrapeCrackleFilter: BiquadFilterNode | null = null;
  private scrapeNoiseBuffer: AudioBuffer | null = null;
  private scrapeSource: AudioBufferSourceNode | null = null;
  private scrapeCrackleSource: AudioBufferSourceNode | null = null;

  // Flat Tire / Puncture Rhythmic Flapping & Metal Rim Grinding
  private flatTireGain: GainNode | null = null;
  private flatTireFilter: BiquadFilterNode | null = null;
  private flatTireOsc: OscillatorNode | null = null;
  private flatTireThumpGain: GainNode | null = null;

  // Pre-baked noise buffers for zero runtime GC / allocation latency
  private backfireBuffer: AudioBuffer | null = null;
  private crashBuffer: AudioBuffer | null = null;
  private radioSquelchBuffer: AudioBuffer | null = null;
  private lastAudioUpdateTimestamp: number = 0;
  private isStationaryAudioActive: boolean = false;
  private lastScrapeIntensity: number = 0;
  private lastHadPuncture: boolean = false;

  constructor() {
    // AudioContext will be initialized on first user interaction
  }

  private createCombustionPeriodicWave(): PeriodicWave | null {
    if (!this.ctx) return null;
    const n = 24;
    const real = new Float32Array(n);
    const imag = new Float32Array(n);
    real[0] = 0;
    imag[0] = 0;

    // Acoustic physical profile of heavy American Competition V8 (cross-plane muscle):
    // Massive visceral fundamental (chest impact), thick manifold growl, heavy mid body, zero shrill treble.
    const amplitudes = [
      0.0,   // 0: DC
      1.35,  // 1: Primary massive cylinder pulse (deep chest punch core)
      1.10,  // 2: Dual exhaust cross-flow rumble
      0.85,  // 3: Cross-plane firing cadence growl
      0.55,  // 4: Cylinder bark
      0.32,  // 5: Low-mid mechanical presence
      0.18,  // 6: Header chamber resonance
      0.09,  // 7
      0.04,  // 8
      0.02,  // 9
      0.008, // 10
      0.004, // 11
    ];
    for (let i = 1; i < Math.min(n, amplitudes.length); i++) {
      imag[i] = amplitudes[i];
    }
    return this.ctx.createPeriodicWave(real, imag, { disableNormalization: false });
  }

  private createCollectorPeriodicWave(): PeriodicWave | null {
    if (!this.ctx) return null;
    const n = 20;
    const real = new Float32Array(n);
    const imag = new Float32Array(n);
    real[0] = 0;
    imag[0] = 0;

    // High-pressure manifold collector wave for heavy muscle rumble
    const amplitudes = [
      0.0,  // 0: DC
      1.10, // 1: Manifold throat core
      1.25, // 2: Collector merge rumble
      0.85, // 3: Mid-pressure roar
      0.45, // 4
      0.22, // 5
      0.08, // 6
      0.02, // 7
    ];
    for (let i = 1; i < Math.min(n, amplitudes.length); i++) {
      imag[i] = amplitudes[i];
    }
    return this.ctx.createPeriodicWave(real, imag, { disableNormalization: false });
  }

  public init(): void {
    if (this.isInitialized) return;

    try {
      const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      this.ctx = new AudioContextClass();

      // Master Gain: clean headroom to prevent DAC hard-clipping
      this.masterGain = this.ctx.createGain();
      this.masterGain.gain.setValueAtTime(0.40, this.ctx.currentTime);
      this.masterGain.connect(this.ctx.destination);

      // Studio-grade transparent Dynamics Compressor / Fast Safety Limiter
      // Ultra-fast attack (3ms) and soft knee clamp transient overshoots before the DAC, eliminating digital crackle
      this.compressor = this.ctx.createDynamicsCompressor();
      this.compressor.threshold.setValueAtTime(-5, this.ctx.currentTime);
      this.compressor.knee.setValueAtTime(10, this.ctx.currentTime);
      this.compressor.ratio.setValueAtTime(5.0, this.ctx.currentTime);
      this.compressor.attack.setValueAtTime(0.003, this.ctx.currentTime);
      this.compressor.release.setValueAtTime(0.15, this.ctx.currentTime);
      this.compressor.connect(this.masterGain);

      // Dedicated Competition Racing Engine Bus (balanced linear authority)
      this.engineBusGain = this.ctx.createGain();
      this.engineBusGain.gain.setValueAtTime(0.88, this.ctx.currentTime);
      this.engineBusGain.connect(this.compressor);

      // Rev Limiter Staccato Gate (cuts engine combustion instantly on redline)
      this.revLimiterGain = this.ctx.createGain();
      this.revLimiterGain.gain.setValueAtTime(1.0, this.ctx.currentTime);
      this.revLimiterGain.connect(this.engineBusGain);

      // Deep American Exhaust Chamber Resonator (REACTIVATED)
      this.exhaustResonance = this.ctx.createBiquadFilter();
      this.exhaustResonance.type = 'peaking';
      this.exhaustResonance.frequency.setValueAtTime(230, this.ctx.currentTime);
      this.exhaustResonance.Q.setValueAtTime(0.8, this.ctx.currentTime);
      this.exhaustResonance.gain.setValueAtTime(2.0, this.ctx.currentTime);

      // Visceral Sub-Bass / Exhaust Pressure Punch Resonator (REACTIVATED)
      this.exhaustBassPunch = this.ctx.createBiquadFilter();
      this.exhaustBassPunch.type = 'peaking';
      this.exhaustBassPunch.frequency.setValueAtTime(75, this.ctx.currentTime);
      this.exhaustBassPunch.Q.setValueAtTime(0.9, this.ctx.currentTime);
      this.exhaustBassPunch.gain.setValueAtTime(2.2, this.ctx.currentTime);

      // Warm Engine low-pass filter (REACTIVATED)
      this.engineFilter = this.ctx.createBiquadFilter();
      this.engineFilter.type = 'lowpass';
      this.engineFilter.frequency.setValueAtTime(620, this.ctx.currentTime);
      this.engineFilter.Q.setValueAtTime(0.9, this.ctx.currentTime);

      // Linear Acoustic Filter Chain:
      this.exhaustResonance.connect(this.exhaustBassPunch);
      this.exhaustBassPunch.connect(this.engineFilter);
      this.engineFilter.connect(this.revLimiterGain);

      // Generate physical cylinder combustion wave and collector wave
      this.combustionWave = this.createCombustionPeriodicWave();
      this.collectorWave = this.createCollectorPeriodicWave();

      // Branch A: Oscillator 1: Primary American V8 ignition pulse train (2.25 pulses per crank revolution)
      this.oscBase = this.ctx.createOscillator();
      if (this.combustionWave) {
        this.oscBase.setPeriodicWave(this.combustionWave);
      } else {
        this.oscBase.type = 'triangle';
      }
      this.oscBase.frequency.setValueAtTime(37.5, this.ctx.currentTime); // 37.5 Hz = deep 1000 RPM American V8 idle
      this.gainBase = this.ctx.createGain();
      this.gainBase.gain.setValueAtTime(0.70, this.ctx.currentTime);
      this.oscBase.connect(this.gainBase);
      this.gainBase.connect(this.exhaustResonance);
      this.oscBase.start();

      // Branch A: Oscillator 2: Exhaust collector resonance (Collector wave, 2x order harmonic growl)
      this.oscHarmonic1 = this.ctx.createOscillator();
      if (this.collectorWave) {
        this.oscHarmonic1.setPeriodicWave(this.collectorWave);
      } else if (this.combustionWave) {
        this.oscHarmonic1.setPeriodicWave(this.combustionWave);
      } else {
        this.oscHarmonic1.type = 'triangle';
      }
      this.oscHarmonic1.frequency.setValueAtTime(75, this.ctx.currentTime);
      this.gainH1 = this.ctx.createGain();
      this.gainH1.gain.setValueAtTime(0.48, this.ctx.currentTime);
      this.oscHarmonic1.connect(this.gainH1);
      this.gainH1.connect(this.exhaustResonance);
      this.oscHarmonic1.start();

      // Branch A: Oscillator 3: Cylinder firing harmonic (3.0x pure integer harmonic, zero intermodulation beating)
      this.oscHarmonic2 = this.ctx.createOscillator();
      this.oscHarmonic2.type = 'triangle';
      this.oscHarmonic2.frequency.setValueAtTime(112.5, this.ctx.currentTime);
      this.gainH2 = this.ctx.createGain();
      this.gainH2.gain.setValueAtTime(0.28, this.ctx.currentTime);
      this.oscHarmonic2.connect(this.gainH2);
      this.gainH2.connect(this.exhaustResonance);
      this.oscHarmonic2.start();

      // Branch A: Oscillator 4: Big-block Airbox Intake Roar (Deep induction growl)
      this.oscIntake = this.ctx.createOscillator();
      this.oscIntake.type = 'triangle';
      this.oscIntake.frequency.setValueAtTime(37.5, this.ctx.currentTime);
      this.intakeFilter = this.ctx.createBiquadFilter();
      this.intakeFilter.type = 'lowpass';
      this.intakeFilter.frequency.setValueAtTime(260, this.ctx.currentTime);
      this.intakeFilter.Q.setValueAtTime(1.2, this.ctx.currentTime);
      this.gainIntake = this.ctx.createGain();
      this.gainIntake.gain.setValueAtTime(0.001, this.ctx.currentTime);
      this.oscIntake.connect(this.intakeFilter);
      this.intakeFilter.connect(this.gainIntake);
      this.gainIntake.connect(this.exhaustResonance);
      this.oscIntake.start();

      // Branch A: Oscillator 5: Sub-bass engine block physical displacement (REACTIVATED)
      this.oscSub = this.ctx.createOscillator();
      this.oscSub.type = 'sine';
      this.oscSub.frequency.setValueAtTime(18.75, this.ctx.currentTime);
      this.gainSub = this.ctx.createGain();
      this.gainSub.gain.setValueAtTime(0.70, this.ctx.currentTime);
      this.oscSub.connect(this.gainSub);
      this.gainSub.connect(this.revLimiterGain);
      this.oscSub.start();



      // Flat Tire Rhythmic Grinding and Flapping Loop
      this.setupFlatTireSound();

      // Pre-bake staccato rev-limiter bark buffer: pure visceral harmonic cylinder shockwave, ZERO white noise/static
      const barkSize = Math.floor(this.ctx.sampleRate * 0.045);
      this.limiterBarkBuffer = this.ctx.createBuffer(1, barkSize, this.ctx.sampleRate);
      const barkData = this.limiterBarkBuffer.getChannelData(0);
      for (let i = 0; i < barkSize; i++) {
        const tSec = i / this.ctx.sampleRate;
        const env = Math.exp(-tSec / 0.012);
        // Deep acoustic cylinder detonation wave: primary 85 Hz punch + 170 Hz manifold body (no noise generator)
        const wave = Math.sin(2 * Math.PI * 85 * tSec) * 0.7 + Math.sin(2 * Math.PI * 170 * tSec) * 0.3;
        barkData[i] = wave * env;
      }

      // Pre-bake backfire buffer: deep resonant pressure thump without white noise
      const bfSize = Math.floor(this.ctx.sampleRate * 0.14);
      this.backfireBuffer = this.ctx.createBuffer(1, bfSize, this.ctx.sampleRate);
      const bfData = this.backfireBuffer.getChannelData(0);
      for (let i = 0; i < bfSize; i++) {
        const tSec = i / this.ctx.sampleRate;
        const env = Math.exp(-tSec / 0.024);
        bfData[i] = (Math.sin(2 * Math.PI * 90 * tSec) * 0.65 + Math.sin(2 * Math.PI * 180 * tSec) * 0.35) * env;
      }

      // Pre-bake crash crunch noise buffer (0.4s)
      const crSize = Math.floor(this.ctx.sampleRate * 0.4);
      this.crashBuffer = this.ctx.createBuffer(1, crSize, this.ctx.sampleRate);
      const crData = this.crashBuffer.getChannelData(0);
      for (let i = 0; i < crSize; i++) {
        crData[i] = (Math.random() * 2 - 1) * Math.exp(-i / (this.ctx.sampleRate * 0.08));
      }

      // Pre-bake VHF radio squelch chirp buffer (0.09s)
      const sqSize = Math.floor(this.ctx.sampleRate * 0.09);
      this.radioSquelchBuffer = this.ctx.createBuffer(1, sqSize, this.ctx.sampleRate);
      const sqData = this.radioSquelchBuffer.getChannelData(0);
      for (let i = 0; i < sqSize; i++) {
        sqData[i] = (Math.random() * 2 - 1) * 0.45;
      }

      this.isInitialized = true;
    } catch (e) {
      console.warn('Web Audio could not initialize automatically:', e);
    }
  }

  private playStaccatoBark(time: number): void {
    if (!this.ctx || !this.limiterBarkBuffer || !this.engineBusGain) return;
    try {
      const src = this.ctx.createBufferSource();
      src.buffer = this.limiterBarkBuffer;

      const bFilter = this.ctx.createBiquadFilter();
      bFilter.type = 'lowpass';
      bFilter.frequency.setValueAtTime(260, time);
      bFilter.Q.setValueAtTime(1.4, time);

      const bGain = this.ctx.createGain();
      bGain.gain.setValueAtTime(0.25, time);
      bGain.gain.exponentialRampToValueAtTime(0.001, time + 0.045);

      src.connect(bFilter);
      bFilter.connect(bGain);
      bGain.connect(this.engineBusGain);

      src.start(time);
      src.stop(time + 0.05);
    } catch {}
  }

  private makeDistortionCurve(amount: number): Float32Array {
    const nSamples = 44100;
    const curve = new Float32Array(nSamples);
    const normFactor = 1 / Math.tanh(amount);
    for (let i = 0; i < nSamples; ++i) {
      const x = (i * 2) / nSamples - 1;
      // Smooth monotonic high-SPL manifold saturation (eliminates intermodulation buzz and edge clipping)
      curve[i] = Math.tanh(x * amount) * normFactor;
    }
    return curve;
  }

  private setupTireScreech(): void {
    if (!this.ctx || !this.masterGain) return;

    // Create 2 seconds of pink/white noise for multi-band tire friction
    const bufferSize = this.ctx.sampleRate * 2;
    this.screechNoiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = this.screechNoiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * 0.7;
    }
    // Seamless Hann window taper to eliminate 2-second loop click/interference
    const screechFade = 2048;
    for (let i = 0; i < screechFade; i++) {
      const w = 0.5 * (1 - Math.cos((i * Math.PI) / screechFade));
      data[i] *= w;
      data[bufferSize - 1 - i] *= w;
    }

    // 1. Mid-Band Screech (800 - 2400 Hz elastic rubber peel)
    this.screechFilter = this.ctx.createBiquadFilter();
    this.screechFilter.type = 'bandpass';
    this.screechFilter.frequency.setValueAtTime(1400, this.ctx.currentTime);
    this.screechFilter.Q.setValueAtTime(3.8, this.ctx.currentTime);
    this.screechGain = this.ctx.createGain();
    this.screechGain.gain.setValueAtTime(0, this.ctx.currentTime);
    this.screechFilter.connect(this.screechGain);
    this.screechGain.connect(this.masterGain);

    // 2. Low-Band Asphalt Scrub Rumble (120 - 450 Hz contact patch vibration)
    this.tireRumbleFilter = this.ctx.createBiquadFilter();
    this.tireRumbleFilter.type = 'lowpass';
    this.tireRumbleFilter.frequency.setValueAtTime(260, this.ctx.currentTime);
    this.tireRumbleGain = this.ctx.createGain();
    this.tireRumbleGain.gain.setValueAtTime(0, this.ctx.currentTime);
    this.tireRumbleFilter.connect(this.tireRumbleGain);
    this.tireRumbleGain.connect(this.masterGain);

    this.startScreechLoop();
  }

  private startScreechLoop(): void {
    if (!this.ctx || !this.screechNoiseBuffer || !this.screechFilter) return;
    this.screechSource = this.ctx.createBufferSource();
    this.screechSource.buffer = this.screechNoiseBuffer;
    this.screechSource.loop = true;

    this.screechSource.connect(this.screechFilter);
    if (this.tireRumbleFilter) this.screechSource.connect(this.tireRumbleFilter);

    this.screechSource.start();
  }

  private setupScrapeSound(): void {
    if (!this.ctx || !this.masterGain) return;

    // 1. High-frequency metallic friction noise buffer (1.5s loop with rapid micro-irregularities)
    const bufferSize = Math.floor(this.ctx.sampleRate * 1.5);
    this.scrapeNoiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = this.scrapeNoiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      const raw = (Math.random() * 2 - 1);
      data[i] = raw * 0.55;
    }
    // Seamless Hann window taper to eliminate loop boundary clicks
    const scrapeFade = 2048;
    for (let i = 0; i < scrapeFade; i++) {
      const w = 0.5 * (1 - Math.cos((i * Math.PI) / scrapeFade));
      data[i] *= w;
      data[bufferSize - 1 - i] *= w;
    }

    // Resonant bandpass filter (metal grinding timbre)
    this.scrapeFilter = this.ctx.createBiquadFilter();
    this.scrapeFilter.type = 'bandpass';
    this.scrapeFilter.frequency.setValueAtTime(3200, this.ctx.currentTime);
    this.scrapeFilter.Q.setValueAtTime(4.2, this.ctx.currentTime);

    this.scrapeGain = this.ctx.createGain();
    this.scrapeGain.gain.setValueAtTime(0, this.ctx.currentTime);

    this.scrapeFilter.connect(this.scrapeGain);
    this.scrapeGain.connect(this.masterGain);

    this.startScrapeLoop();
  }

  private startScrapeLoop(): void {
    if (!this.ctx || !this.scrapeNoiseBuffer) return;
    this.scrapeSource = this.ctx.createBufferSource();
    this.scrapeSource.buffer = this.scrapeNoiseBuffer;
    this.scrapeSource.loop = true;
    if (this.scrapeFilter) {
      this.scrapeSource.connect(this.scrapeFilter);
    }
    this.scrapeSource.start();
  }


  /**
   * Real-time continuous scraping / metal friction sound modulation
   * @param intensity 0.0 to 1.0 friction force
   * @param speedKmh vehicle speed in km/h
   */
  public updateScrape(_intensity: number, _speedKmh: number): void {
    // Completely silenced per user specification
    return;
  }

  public resume(): void {
    if (!this.isInitialized) {
      this.init();
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  /**
   * Update engine sound parameters every frame
   * @param rpm Current engine RPM (e.g. 1000 - 9500)
   * @param throttle Throttle pedal position (0.0 - 1.0)
   * @param slipRatio Lateral/longitudinal tire slip factor (0.0 - 1.0)
   * @param speed Car speed in m/s
   * @param engineHealth Factor 0.0 to 1.0
   */
  public update(rpm: number, throttle: number, slipRatio: number, speed: number, engineHealth: number = 1.0): void {
    if (!this.isInitialized || !this.ctx || this.isMuted) return;

    const now = performance.now();
    // Throttle high-frequency AudioParam updates to ~38 Hz (26ms).
    // Web Audio's setTargetAtTime seamlessly and continuously interpolates across updates.
    const dt = Math.min(0.1, (now - this.lastAudioUpdateTimestamp) * 0.001);
    this.lastAudioUpdateTimestamp = now;

    const t = this.ctx.currentTime;

    // Competition American Muscle V8 firing profile (2.25 pulses per crank rev):
    const rps = rpm / 60;
    const targetBaseFreq = Math.max(35, rps * 2.25);
    const targetRpmNorm = Math.min(1.0, Math.max(0.0, (rpm - 1000) / (9500 - 1000)));
    const targetThrottleNorm = Math.min(1.0, Math.max(0.0, throttle));

    // Continuous 1st-order low-pass filter in JS: eliminates discrete frame jumps and phase slope kinks
    const alpha = Math.min(1.0, dt * 24.0);
    this.smoothBaseFreq += (targetBaseFreq - this.smoothBaseFreq) * alpha;
    this.smoothRpmNorm += (targetRpmNorm - this.smoothRpmNorm) * alpha;
    this.smoothThrottleNorm += (targetThrottleNorm - this.smoothThrottleNorm) * alpha;

    const baseFreq = this.smoothBaseFreq;
    const rpmNorm = this.smoothRpmNorm;
    const throttleNorm = this.smoothThrottleNorm;
    const throttleSq = Math.pow(throttleNorm, 1.25);

    // Dynamic American Muscle Oscillator Frequency Modulation
    // Using current render time (t) provides mathematically seamless C-infinity continuous interpolation
    // completely eliminating future-timestamp schedule holds and phase jitter
    if (this.oscBase) {
      this.oscBase.frequency.setTargetAtTime(baseFreq, t, 0.04);
    }
    if (this.oscHarmonic1) {
      this.oscHarmonic1.frequency.setTargetAtTime(baseFreq * 2.0, t, 0.04);
    }
    if (this.oscHarmonic2) {
      this.oscHarmonic2.frequency.setTargetAtTime(baseFreq * 3.0, t, 0.04);
    }
    if (this.oscIntake) {
      this.oscIntake.frequency.setTargetAtTime(baseFreq * 1.0, t, 0.045);
    }
    if (this.oscSub) {
      this.oscSub.frequency.setTargetAtTime(baseFreq * 0.5, t, 0.04);
    }

    // Branch A Mix: massive guttural American muscle roar with reinforced deep bass (clean linear gain staging)
    if (this.gainBase) {
      const baseVol = 0.65 + 0.18 * rpmNorm + 0.20 * throttleSq;
      this.gainBase.gain.setTargetAtTime(baseVol, t, 0.035);
    }
    if (this.gainH1) {
      const h1Vol = 0.42 + 0.16 * rpmNorm + 0.14 * throttleSq;
      this.gainH1.gain.setTargetAtTime(h1Vol, t, 0.035);
    }
    if (this.gainH2) {
      const h2Vol = 0.28 + 0.12 * rpmNorm + 0.08 * throttleSq;
      this.gainH2.gain.setTargetAtTime(h2Vol, t, 0.035);
    }
    if (this.gainIntake && this.intakeFilter) {
      const intakeVol = throttleSq * (0.24 + 0.14 * rpmNorm);
      this.gainIntake.gain.setTargetAtTime(Math.max(0.001, intakeVol), t, 0.04);
      this.intakeFilter.frequency.setTargetAtTime(240 + rpmNorm * 220 + throttleNorm * 110, t, 0.045);
    }
    if (this.gainSub) {
      const subVol = 0.58 + 0.22 * throttleSq;
      this.gainSub.gain.setTargetAtTime(subVol, t, 0.035);
    }

    // Visceral Sub-Bass & Exhaust Pressure Punch (clean warm punch, gentle Q)
    if (this.exhaustBassPunch) {
      const bassPunchFreq = 70 + rpmNorm * 45 + throttleNorm * 20;
      this.exhaustBassPunch.frequency.setTargetAtTime(bassPunchFreq, t, 0.045);
      this.exhaustBassPunch.gain.setTargetAtTime(2.0 + throttleSq * 1.5, t, 0.045);
    }

    // American Exhaust chamber resonance (warm 230 Hz - 440 Hz body)
    if (this.exhaustResonance) {
      const resonanceFreq = 230 + rpmNorm * 180 + throttleNorm * 80;
      this.exhaustResonance.frequency.setTargetAtTime(resonanceFreq, t, 0.045);
      this.exhaustResonance.gain.setTargetAtTime(1.8 + throttleNorm * 1.2, t, 0.045);
    }

    // Engine lowpass filter (warm cutoff 620 Hz to 1850 Hz - strictly zero shrill buzzers)
    if (this.engineFilter) {
      const minCutoff = 620;
      const maxCutoff = 1850;
      const targetCutoff = minCutoff + (maxCutoff - minCutoff) * Math.pow(Math.max(throttleNorm, 0.30 * rpmNorm), 1.15);
      this.engineFilter.frequency.setTargetAtTime(targetCutoff, t, 0.045);
    }
  }

  /**
   * Sound effect for gear changes, rev-limiters and lift-off backfires
   * Intentionally silenced per user specification: ZERO pops, bangs, or backfires
   */
  public triggerBackfire(_isHighRpm: boolean = false): void {
    // Zero-backfire acoustic profile: completely muted
    return;
  }

  /**
   * Collision sound effect with volume and pitch scaled by impact force (zero-allocation)
   */
  public triggerCrash(impactForce: number): void {
    if (!this.isInitialized || !this.ctx || this.isMuted) return;

    const t = this.ctx.currentTime;
    const normalizedForce = Math.min(1.0, Math.max(0.1, impactForce / 35));

    // Low frequency punch
    const osc = this.ctx.createOscillator();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(140, t);
    osc.frequency.exponentialRampToValueAtTime(30, t + 0.35);

    const oscGain = this.ctx.createGain();
    oscGain.gain.setValueAtTime(normalizedForce * 0.7, t);
    oscGain.gain.exponentialRampToValueAtTime(0.001, t + 0.4);

    osc.connect(oscGain);
    oscGain.connect(this.masterGain!);
    osc.start(t);
    osc.stop(t + 0.4);

    // Crunch noise using pre-baked buffer
    const noise = this.ctx.createBufferSource();
    if (this.crashBuffer) {
      noise.buffer = this.crashBuffer;
    }

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(800, t);
    filter.Q.setValueAtTime(2.0, t);

    const noiseGain = this.ctx.createGain();
    noiseGain.gain.setValueAtTime(normalizedForce * 0.8, t);
    noiseGain.gain.exponentialRampToValueAtTime(0.001, t + 0.4);

    noise.connect(filter);
    filter.connect(noiseGain);
    noiseGain.connect(this.masterGain!);
    noise.start(t);
  }

  /**
   * Sound effect for pneumatic hydraulic car lift jacks (hiss & clank)
   */
  public triggerPneumaticJack(isUp: boolean): void {
    if (!this.isInitialized || !this.ctx || this.isMuted) return;

    const t = this.ctx.currentTime;
    // Compressed air burst (noise with bandpass sweep)
    const bufferSize = Math.floor(this.ctx.sampleRate * 0.45);
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (this.ctx.sampleRate * 0.12));
    }

    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;

    const filter = this.ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(isUp ? 2200 : 1200, t);
    filter.frequency.exponentialRampToValueAtTime(isUp ? 600 : 300, t + 0.35);
    filter.Q.setValueAtTime(3.0, t);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.35, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.42);

    noise.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain!);
    noise.start(t);

    // Mechanical jack latch clank
    const clankOsc = this.ctx.createOscillator();
    const clankGain = this.ctx.createGain();
    clankOsc.type = 'triangle';
    clankOsc.frequency.setValueAtTime(isUp ? 380 : 180, t + 0.05);
    clankOsc.frequency.exponentialRampToValueAtTime(80, t + 0.18);

    clankGain.gain.setValueAtTime(0.4, t + 0.05);
    clankGain.gain.exponentialRampToValueAtTime(0.001, t + 0.2);

    clankOsc.connect(clankGain);
    clankGain.connect(this.masterGain!);
    clankOsc.start(t + 0.05);
    clankOsc.stop(t + 0.22);
  }

  /**
   * Sound effect for high-speed pneumatic impact wrench unbolting/bolting wheel nuts
   */
  public triggerWheelGunRattle(): void {
    if (!this.isInitialized || !this.ctx || this.isMuted) return;

    const t = this.ctx.currentTime;
    // Rapid rat-tat-tat pulses
    const pulseCount = 6;
    for (let p = 0; p < pulseCount; p++) {
      const pt = t + p * 0.038;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(1400 + Math.random() * 400, pt);
      osc.frequency.exponentialRampToValueAtTime(350, pt + 0.03);

      gain.gain.setValueAtTime(0.22, pt);
      gain.gain.exponentialRampToValueAtTime(0.001, pt + 0.035);

      osc.connect(gain);
      gain.connect(this.masterGain!);
      osc.start(pt);
      osc.stop(pt + 0.04);
    }
  }

  private setupFlatTireSound(): void {
    if (!this.ctx || !this.masterGain) return;

    // Flat tire filter and gain initialized silently
    this.flatTireFilter = this.ctx.createBiquadFilter();
    this.flatTireFilter.type = 'bandpass';
    this.flatTireFilter.frequency.setValueAtTime(450, this.ctx.currentTime);
    this.flatTireFilter.Q.setValueAtTime(2.5, this.ctx.currentTime);

    this.flatTireGain = this.ctx.createGain();
    this.flatTireGain.gain.setValueAtTime(0, this.ctx.currentTime);
    this.flatTireFilter.connect(this.flatTireGain);
    this.flatTireGain.connect(this.masterGain);

    this.flatTireThumpGain = this.ctx.createGain();
    this.flatTireThumpGain.gain.setValueAtTime(0, this.ctx.currentTime);
    this.flatTireThumpGain.connect(this.masterGain);
  }

  /**
   * Real-time continuous flat tire flapping / rim grinding sound modulation
   */
  public updateFlatTireSound(hasPuncture: boolean, speedMs: number): void {
    if (!this.isInitialized || !this.ctx || this.isMuted) return;
    if (!hasPuncture && !this.lastHadPuncture) return;
    this.lastHadPuncture = hasPuncture;

    const t = this.ctx.currentTime;
    const safeTime = t + 0.008;
    const speedKmh = speedMs * 3.6;

    if (hasPuncture && speedKmh > 2.0) {
      if (!this.flatTireOsc && this.ctx) {
        this.flatTireOsc = this.ctx.createOscillator();
        this.flatTireOsc.type = 'sawtooth';
        this.flatTireOsc.frequency.setValueAtTime(14, safeTime);
        const thumpFilter = this.ctx.createBiquadFilter();
        thumpFilter.type = 'lowpass';
        thumpFilter.frequency.setValueAtTime(160, safeTime);
        this.flatTireOsc.connect(thumpFilter);
        if (this.flatTireThumpGain) thumpFilter.connect(this.flatTireThumpGain);
        this.flatTireOsc.start();
      }

      const flapFreq = Math.max(3, Math.min(35, speedMs * 2.8));
      const targetGain = Math.min(0.65, 0.15 + (speedKmh / 50.0) * 0.45);

      if (this.flatTireOsc) {
        this.flatTireOsc.frequency.setTargetAtTime(flapFreq, safeTime, 0.04);
      }
      if (this.flatTireThumpGain) {
        this.flatTireThumpGain.gain.setTargetAtTime(targetGain * 0.75, safeTime, 0.04);
      }
      if (this.flatTireGain) {
        this.flatTireGain.gain.setTargetAtTime(targetGain * 0.55, safeTime, 0.04);
      }
      if (this.flatTireFilter) {
        const centerFreq = 320 + speedKmh * 18.0;
        this.flatTireFilter.frequency.setTargetAtTime(centerFreq, safeTime, 0.05);
      }
    } else {
      if (this.flatTireThumpGain) {
        this.flatTireThumpGain.gain.setTargetAtTime(0, safeTime, 0.035);
      }
      if (this.flatTireGain) {
        this.flatTireGain.gain.setTargetAtTime(0, safeTime, 0.035);
      }
    }
  }

  /**
   * Explosive pneumatic tire blowout sound effect ("BANG! PSHHHHH!")
   */
  public triggerTireBlowout(): void {
    if (!this.isInitialized || !this.ctx || this.isMuted) return;

    const t = this.ctx.currentTime;

    // 1. Explosive Shockwave Burst (Heavy Low-Mid Transient Pop)
    const popOsc = this.ctx.createOscillator();
    const popGain = this.ctx.createGain();
    popOsc.type = 'sawtooth';
    popOsc.frequency.setValueAtTime(320, t);
    popOsc.frequency.exponentialRampToValueAtTime(35, t + 0.18);

    popGain.gain.setValueAtTime(0.85, t);
    popGain.gain.exponentialRampToValueAtTime(0.001, t + 0.22);

    popOsc.connect(popGain);
    popGain.connect(this.masterGain!);
    popOsc.start(t);
    popOsc.stop(t + 0.25);

    // 2. High-Pressure Air Decompression Hiss ("PSHHHHH!")
    const hissLen = Math.floor(this.ctx.sampleRate * 0.85);
    const hissBuffer = this.ctx.createBuffer(1, hissLen, this.ctx.sampleRate);
    const hissData = hissBuffer.getChannelData(0);
    for (let i = 0; i < hissLen; i++) {
      hissData[i] = (Math.random() * 2 - 1) * Math.exp(-i / (this.ctx.sampleRate * 0.28));
    }

    const hissSource = this.ctx.createBufferSource();
    hissSource.buffer = hissBuffer;

    const hissFilter = this.ctx.createBiquadFilter();
    hissFilter.type = 'highpass';
    hissFilter.frequency.setValueAtTime(1800, t);
    hissFilter.frequency.exponentialRampToValueAtTime(600, t + 0.7);

    const hissGain = this.ctx.createGain();
    hissGain.gain.setValueAtTime(0.6, t);
    hissGain.gain.exponentialRampToValueAtTime(0.001, t + 0.8);

    hissSource.connect(hissFilter);
    hissFilter.connect(hissGain);
    hissGain.connect(this.masterGain!);
    hissSource.start(t);

    // 3. Metallic Rim Hit Transient
    const rimOsc = this.ctx.createOscillator();
    const rimGain = this.ctx.createGain();
    rimOsc.type = 'square';
    rimOsc.frequency.setValueAtTime(980, t + 0.02);
    rimOsc.frequency.exponentialRampToValueAtTime(140, t + 0.14);

    rimGain.gain.setValueAtTime(0.45, t + 0.02);
    rimGain.gain.exponentialRampToValueAtTime(0.001, t + 0.15);

    rimOsc.connect(rimGain);
    rimGain.connect(this.masterGain!);
    rimOsc.start(t + 0.02);
    rimOsc.stop(t + 0.16);
  }

  /**
   * Pit stop completion sound
   */
  public triggerPitChime(): void {
    if (!this.isInitialized || !this.ctx || this.isMuted) return;

    const notes = [523.25, 659.25, 783.99, 1046.5]; // C, E, G, High C
    const t = this.ctx.currentTime;

    notes.forEach((freq, idx) => {
      const osc = this.ctx!.createOscillator();
      const gain = this.ctx!.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, t + idx * 0.08);

      gain.gain.setValueAtTime(0.2, t + idx * 0.08);
      gain.gain.exponentialRampToValueAtTime(0.001, t + idx * 0.08 + 0.25);

      osc.connect(gain);
      gain.connect(this.masterGain!);
      osc.start(t + idx * 0.08);
      osc.stop(t + idx * 0.08 + 0.3);
    });
  }

  /**
   * Synthesize authentic F1 Pit Radio communications with VHF static, bandpass filter & roger beeps
   */
  public triggerPitRadio(_cue: 'box' | 'tyres' | 'go' | 'puncture'): void {
    // Deactivated per user request
    return;
  }

  public toggleMute(): boolean {
    this.isMuted = !this.isMuted;
    if (this.masterGain && this.ctx) {
      this.masterGain.gain.setValueAtTime(this.isMuted ? 0 : 0.40, this.ctx.currentTime);
    }
    return this.isMuted;
  }

  public getMuted(): boolean {
    return this.isMuted;
  }

  public pause(): void {
    if (this.ctx && this.ctx.state === 'running') {
      this.ctx.suspend().catch(() => {});
    }
  }

  public dispose(): void {
    if (this.ctx && this.ctx.state !== 'closed') {
      try {
        if (this.oscBase) { this.oscBase.stop(); this.oscBase.disconnect(); }
        if (this.oscHarmonic1) { this.oscHarmonic1.stop(); this.oscHarmonic1.disconnect(); }
        if (this.oscHarmonic2) { this.oscHarmonic2.stop(); this.oscHarmonic2.disconnect(); }
        if (this.oscIntake) { this.oscIntake.stop(); this.oscIntake.disconnect(); }
        if (this.oscSub) { this.oscSub.stop(); this.oscSub.disconnect(); }
        if (this.gearWhineOsc) { this.gearWhineOsc.stop(); this.gearWhineOsc.disconnect(); }
        if (this.f1WhineOsc) { this.f1WhineOsc.stop(); this.f1WhineOsc.disconnect(); }
        if (this.flatTireOsc) { this.flatTireOsc.stop(); this.flatTireOsc.disconnect(); }
        if (this.screechSource) { this.screechSource.stop(); this.screechSource.disconnect(); }
        if (this.scrapeSource) { this.scrapeSource.stop(); this.scrapeSource.disconnect(); }
        if (this.revLimiterGain) { this.revLimiterGain.disconnect(); }
        if (this.exhaustBassPunch) { this.exhaustBassPunch.disconnect(); }
        if (this.distortionPreGain) { this.distortionPreGain.disconnect(); }
        if (this.distortionPostGain) { this.distortionPostGain.disconnect(); }
      } catch {
        // Safe catch for already stopped nodes
      }
      this.ctx.close().catch(() => {});
      this.ctx = null;
    }
    this.isInitialized = false;
  }
}
