'use strict';
class MotionPlayer {
  constructor(load) {
    this.load = load; this.sequence = 0; this.cache = new Map(); this.timer = null;
    this.$ = selector => document.querySelector(selector);
    this.$('#motionPrevious').onclick = () => this.setStep(this.index - 1);
    this.$('#motionNext').onclick = () => this.setStep(this.index + 1);
    this.$('#motionRange').oninput = event => this.setStep(Number(event.target.value));
    this.$('#motionPlay').onclick = () => this.timer ? this.pause() : this.play();
    this.$('#motionSpeed').onchange = () => { if (this.timer) { this.pause(); this.play(); } };
  }
  pause() { clearInterval(this.timer); this.timer = null; this.$('#motionPlay').textContent = 'Play'; }
  play() {
    if (!this.attempt?.steps.length) return;
    if (this.index === this.attempt.steps.length) this.setStep(0);
    this.$('#motionPlay').textContent = 'Pause';
    this.timer = setInterval(() => {
      this.setStep(this.index + 1);
      if (this.index === this.attempt.steps.length) this.pause();
    }, Number(this.$('#motionSpeed').value));
  }
  async show(url, attempt, palette) {
    this.pause(); const sequence = ++this.sequence; this.attempt = null;
    this.$('#motionFrames').hidden = true;
    this.$('#motionStatus').textContent = 'Loading recorded actions…';
    try {
      if (!this.cache.has(url)) this.cache.set(url, this.load(url).catch(error => { this.cache.delete(url); throw error; }));
      const data = await this.cache.get(url);
      if (sequence !== this.sequence) return;
      this.attempt = data.attempts.find(row => row.attempt === Number(attempt));
      if (!this.attempt) throw new Error('No action log is available for this attempt.');
      this.palette = palette.map(color => [1,3,5].map(start => parseInt(color.slice(start,start + 2),16)));
      this.frames = [this.attempt.initial_frame];
      for (const step of this.attempt.steps) {
        let next = this.frames.at(-1);
        for (const [start, values] of step.patch) next = next.slice(0,start) + values + next.slice(start + values.length);
        if (next.length !== 4096 || /[^0-9a-f]/.test(next)) throw new Error('Invalid frame data.');
        this.frames.push(next);
      }
      this.$('#motionRange').max = this.attempt.steps.length;
      this.$('#motionMethod').textContent = data.method + (data.recorded_frame_hashes_verified ? ` ${data.recorded_frame_hashes_verified} archived pixel hashes also checked.` : '');
      this.$('#actionList').replaceChildren();
      const labels = ['Initial screen', ...this.attempt.steps.map((step,index) => `${index + 1} · ${this.actionLabel(step)}`)];
      labels.forEach((label,index) => {
        const button = document.createElement('button'); button.textContent = label;
        button.type = 'button'; button.onclick = () => { this.pause(); this.setStep(index); };
        this.$('#actionList').append(button);
      });
      this.$('#motionFrames').hidden = false; this.setStep(0);
    } catch (error) { if (sequence === this.sequence) this.$('#motionStatus').textContent = error.message; }
  }
  actionLabel(step) { return step.action === 6 ? `Click (${step.x}, ${step.y})` : ({1:'Move up',2:'Move down',3:'Move left',4:'Move right'}[step.action] || `Action ${step.action}`); }
  draw(selector, frame, step) {
    const canvas = this.$(selector), context = canvas.getContext('2d');
    const pixels = context.createImageData(64,64);
    for (let i = 0; i < 4096; i++) {
      const rgb = this.palette[parseInt(frame[i],16)];
      pixels.data.set([...rgb,255], i * 4);
    }
    context.putImageData(pixels,0,0);
    if (step?.action === 6) {
      context.beginPath(); context.strokeStyle = '#ff3e61'; context.lineWidth = .55;
      context.arc(step.x + .5,step.y + .5,2.1,0,Math.PI * 2); context.stroke();
    }
  }
  setStep(index) {
    if (!this.attempt) return;
    this.index = Math.max(0, Math.min(index, this.attempt.steps.length));
    const step = this.attempt.steps[this.index - 1];
    this.draw('#frameBefore',this.frames[Math.max(0,this.index - 1)],step);
    this.draw('#frameAfter',this.frames[this.index],step);
    this.$('#motionRange').value = this.index;
    this.$('#motionPosition').textContent = this.index ? `Action ${this.index} / ${this.attempt.steps.length} · ${this.actionLabel(step)}` : `Initial screen · ${this.attempt.steps.length} recorded actions`;
    this.$('#motionStatus').textContent = step ? `Level ${step.level_before} → ${step.level} · ${step.state} · budget used ${step.used} / ${step.cap}` : `Level ${this.attempt.start_level} · before the first action`;
    this.$('#motionSource').textContent = step ? `${new Date(step.time * 1000).toISOString()} · ${step.source}:${step.source_line}` : '';
    this.$('#motionPrevious').disabled = this.index === 0;
    this.$('#motionNext').disabled = this.index === this.attempt.steps.length;
    this.$('#actionList').querySelectorAll('button').forEach((button,i) => { button.classList.toggle('active',i === this.index); button.setAttribute('aria-current',i === this.index ? 'step' : 'false'); });
  }
}
window.MotionPlayer = MotionPlayer;
