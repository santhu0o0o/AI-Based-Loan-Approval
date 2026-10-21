import { House } from 'lucide-react';
import { Link } from 'react-router-dom';
import { LostArt } from '../components/art.jsx';

export default function NotFound() {
  return (
    <div className="wrap narrow empty-state">
      <LostArt />
      <h1>We can&rsquo;t find that page</h1>
      <p>The link may be old or mistyped. Let&rsquo;s go back to the start.</p>
      <Link to="/" className="btn btn-primary btn-xl">
        <House size={24} aria-hidden="true" />
        Go to the home page
      </Link>
    </div>
  );
}
