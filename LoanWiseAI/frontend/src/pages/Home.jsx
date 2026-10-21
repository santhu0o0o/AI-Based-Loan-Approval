import { ClipboardList, Cpu, ArrowRight, Stamp } from 'lucide-react';
import { Link } from 'react-router-dom';
import { HeroArt } from '../components/art.jsx';
import { Disclaimer } from '../components/bits.jsx';

const STEPS = [
  { icon: ClipboardList, title: 'Answer 11 easy questions', text: 'Mostly taps. A few numbers, like your monthly pay.' },
  { icon: Cpu, title: 'Our computer checks them', text: 'It compares you with 614 people who asked for loans before.' },
  { icon: Stamp, title: 'See your answer, and why', text: 'Likely yes or likely no, how sure we are, and what helped or hurt.' },
];

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <h1 className="hero-title">Will the bank say yes to your home loan?</h1>
          <p className="hero-lede">Answer a few easy questions. We&rsquo;ll show your chances in about one minute.</p>
          <Link to="/check" className="btn btn-primary btn-xl">
            Check my loan chances
            <ArrowRight size={24} aria-hidden="true" />
          </Link>
          <p className="hero-fine">Free. No sign-up. Nothing is sent to any bank.</p>
        </div>
        <div className="hero-visual">
          <HeroArt />
        </div>
      </section>

      <section className="how-strip" aria-labelledby="how-strip-title">
        <h2 id="how-strip-title" className="section-title">
          How it works
        </h2>
        <ol className="steps-row">
          {STEPS.map(({ icon: Icon, title, text }, i) => (
            <li key={title} className="step-tile">
              <span className="step-num" aria-hidden="true">
                {i + 1}
              </span>
              <span className="step-icon" aria-hidden="true">
                <Icon size={28} />
              </span>
              <h3>{title}</h3>
              <p>{text}</p>
            </li>
          ))}
        </ol>
        <p className="how-strip-more">
          <Link to="/how-it-works" className="text-link">
            Read more about how our computer decides
          </Link>
        </p>
      </section>

      <section className="wrap home-disclaimer">
        <Disclaimer />
      </section>
    </>
  );
}
