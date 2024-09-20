import React from "react";
import './App.css';
import cyberjam_logo from './Cyberjam_tilted2.png';
import registerBanner from './CJBannr_3.png';
import sponsors23 from './Sponsors23.png';

const App = () => {
  return (
    <div>
      <Navbar />
      <Home />
      <Sponsors />
      <Register />
      <Cyberjam2023 />
    </div>
  );
};

const Navbar = () => {
  return (
    <nav className="sticky top-0 bg-gray-900 text-white py-4">
      <div className="container mx-auto flex justify-between items-center">
        <a href="#home" className="flex items-center justify-center w-20 h-20 rounded-full">
          <img src={cyberjam_logo} alt="Cyberjam" className="w-full h-full object-cover" />
        </a>
        <div>
          <a href="#sponsors" className="px-4">Sponsor us</a>
          <a href="#register" className="px-4">Register</a>
          <a href="#2023cyberjam" className="px-4">2023 Cyberjam </a>
        </div>
      </div>
    </nav>
  );
};

const Home = () => {
  return (
    <section id="home" className="min-h-screen bg-blue-900 text-white flex items-center justify-center py-16">
      <div className="container text-center mx-1">
        <h1 className="text-5xl font-bold mb-6">Welcome to Cyberjam 2024</h1>
        <p className="text-xl mb-8">A one-of-a-kind collaborative hackathon pushing the boundaries of what's possible with phygital experiences.</p>
        <h2 className="text-3xl font-semibold mb-4">About Cyberjam</h2>
        <p className="text-lg mb-8">Cyberjam 2024 is an immersive hackathon taking place from October 19th to October 27th at <a href="https://1871.com/" target="_blank" rel="noopener noreferrer" className="underline">Chicago's global innovation, 1871</a>. Teams of 5 will work together on phygital experiences combining art, technology, and innovation across five thematic tracks:</p>
        <ul className="list-disc list-inside mb-8">
          <li>AI</li>
          <li>Fashion</li>
          <li>Governance</li>
          <li>Sports/Gaming</li>
          <li>Security & Privacy</li>
        </ul>
        <a href="#register" className="mt-6 inline-block bg-pink-600 py-2 px-4 text-white rounded">Register Now</a>
      </div>
    </section>
  );
};

const Sponsors = () => {
  return (
    <section id="sponsors" className="min-h-screen bg-gray-200 text-gray-900 flex items-center justify-center py-16">
      <div className="container mx-auto text-center">
        <h2 className="text-4xl font-bold mb-6">Sponsor us!</h2>
        <p className="text-lg">Become a sponsor and join us in creating one-of-a-kind experiences. Tailor your sponsorship to our themes and be part of the future of phygital experiences.</p>
        <a href="https://drive.google.com/file/d/11_AF3JkFl6CpIwhPNU2s2Znp-fc7IbmX/view?usp=sharing" className="mt-6 inline-block bg-pink-600 py-2 px-4 text-white rounded">Check out our Sponsor Deck</a>
      </div>
    </section>
  );
};

const Register = () => {
  return (
    <section id="register" className="min-h-screen bg-blue-900 text-white flex items-center justify-center py-16">
      <div className="container mx-auto text-center">
        <h2 className="text-4xl font-bold mb-6">Register for Cyberjam 2024</h2>
        <p className="text-lg mb-8">
          Cyberjam is not your typical hackathon. Our teams are made up of artists, technologists, and wildcards from various fields, coming together to build innovative "phygital" experiences. Are you ready to join the future of creativity and technology?
        </p>
        <a href="https://forms.gle/xCEp1JVBSPCwhGJu7" target="_blank" rel="noopener noreferrer" className="block mb-8">
          <img src={registerBanner} alt="Register for Cyberjam 2024" className="w-full max-w-2xl mx-auto" />
        </a>
        <h3 className="text-3xl font-semibold mb-4">How Cyberjam Works</h3>
        <p className="text-lg mb-4">
          Cyberjam 2024 focuses on bringing together multidisciplinary teams to create immersive "phygital" (physical + digital) experiences. Here’s what you can expect:
        </p>
        
        <h3 className="text-3xl font-semibold mb-4">Multidisciplinary Teams and Roles</h3>
        <p className="text-lg mb-4">We aim to bridge the gap between creatives and technologists. Our teams consist of diverse roles working together on phygital collaborations. Which role do you identify with?</p>
        <ul className="list-disc text-left mb-8">
          <li><strong>Visual Artist:</strong> You create or tell stories through visuals.</li>
          <li><strong>Sound Artist:</strong> You have a passion for sound, music, or composing.</li>
          <li><strong>Software Developer:</strong> You build applications or integrate software into systems.</li>
          <li><strong>Hardware Developer:</strong> You work with physical components and connect them with digital systems.</li>
          <li><strong>Wildcard:</strong> You bring unique skills outside traditional 'hackathon' roles, such as marketing or project management.</li>
        </ul>
        <p className="text-lg mb-8">Together, these multidisciplinary teams work beyond the digital realm to create installations that merge physical and digital worlds, fostering continued collaboration and community engagement.</p>

        <a href="https://forms.gle/xCEp1JVBSPCwhGJu7" target="_blank" rel="noopener noreferrer" className="mt-6 inline-block bg-pink-600 py-2 px-4 text-white rounded">
          Jammer Waitlist Registration
        </a>
        <p className="text-sm m-4">
          Not sure which role fits you best? You will have the chance to select your avatar and define your strengths after completing registration.
        </p>


        <p className="text-lg mt-8"> 
          <a href="https://forms.gle/xCEp1JVBSPCwhGJu7" target="_blank" rel="noopener noreferrer" className="underline">Sign up for the waitlist</a> and we'll be in contact soon with next steps!
        </p>
      </div>
    </section>
  );
};

const Cyberjam2023 = () => {
  return (
    <section id="2023cyberjam" className="min-h-screen bg-gray-100 text-gray-900 flex items-center justify-center py-16">
      <div className="container mx-auto text-center">
        <h2 className="text-4xl font-bold mb-6 text-pink-600">2023: &lt;imnotHackathon&gt; BETA (alpha)</h2>
        <img src={sponsors23} alt="Cyberjam 2023 Sponsors" className="w-full max-w-4xl mx-auto my-8" />
        <p className="text-lg">Check out the highlights from Cyberjam 2023!</p>
        <div className="flex justify-center items-center mt-6">
          <iframe width="939" height="528" src="https://www.youtube.com/embed/Qu6LKDAfDZI" title="ETHChicago presents the 2023 CyberJam" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
        </div>
      </div>
    </section>
  );
}

export default App;