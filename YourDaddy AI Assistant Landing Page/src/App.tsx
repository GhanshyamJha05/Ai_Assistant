import Hero from './components/Hero';
import Features from './components/Features';
import HowItWorks from './components/HowItWorks';
import AISystems from './components/AISystems';
import UseCases from './components/UseCases';
import TechStack from './components/TechStack';
import Stats from './components/Stats';
import SecurityFAQ from './components/SecurityFAQ';
import CTA from './components/CTA';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen bg-slate-900">
      <Hero />
      <Features />
      <HowItWorks />
      <AISystems />
      <UseCases />
      <TechStack />
      <Stats />
      <SecurityFAQ />
      <CTA />
      <Footer />
    </div>
  );
}

export default App;
