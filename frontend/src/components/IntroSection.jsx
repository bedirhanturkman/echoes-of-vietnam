export default function IntroSection({ onBegin }) {
  return (
    <section className="intro-section animate-fade-in">
      <div className="content">
        <h1>Echoes of the Vietnam Frontier</h1>
        <h2>A data sonification artwork that transforms historical war records into music.</h2>
        <p>
          Each event becomes a musical trace. Each cluster becomes a section of the composition.
          The past is not only read — it is listened to.
        </p>
        <button className="primary-btn" onClick={onBegin}>
          Begin the Experience
        </button>
      </div>
    </section>
  );
}
