import React from "react";
import './App.css';

const App = () => {
  return (
    <div>
      <Navbar />
      <Home />
      <About />
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
          <img src="Cyberjam_tilted2.png" alt="Cyberjam" className="w-full h-full object-cover" />
        </a>
        <div>
          <a href="#about" className="px-4">About</a>
          <a href="#sponsors" className="px-4">Sponsors</a>
          <a href="#register" className="px-4">Register</a>
          <a href="#2023cyberjam" className="px-4">2023 Cyberjam </a>
        </div>
      </div>
    </nav>
  );
};

const Home = () => {
  return (
    <section id="home" className="min-h-screen bg-blue-900 text-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-5xl font-bold mb-4">Welcome to Cyberjam 2024</h1>
        <p className="text-xl">A one-of-a-kind collaborative hackathon pushing the boundaries of what's possible with phygital experiences.</p>
        <a href="#register" className="mt-6 inline-block bg-pink-600 py-2 px-4 text-white rounded">Register Now</a>
      </div>
    </section>
  );
};

const About = () => {
  return (
    <section id="about" className="min-h-screen bg-gray-100 text-gray-900 flex items-center justify-center py-16">
      <div className="container mx-auto text-center">
        <h2 className="text-4xl font-bold mb-6">About Cyberjam</h2>
        <p className="text-lg">Cyberjam 2024 is an immersive hackathon taking place from October 19th to October 27th at Chicago 1871. Teams of 5 will work together on phygital experiences combining art, technology, and innovation across five thematic tracks: Governance, Fashion, Security & Privacy, Sports & Gaming, and AI.</p>
      </div>
    </section>
  );
};

const Sponsors = () => {
  return (
    <section id="sponsors" className="min-h-screen bg-gray-200 text-gray-900 flex items-center justify-center py-16">
      <div className="container mx-auto text-center">
        <h2 className="text-4xl font-bold mb-6">Our Sponsors</h2>
        <p className="text-lg">Become a sponsor and join us in creating one-of-a-kind experiences. Tailor your sponsorship to our themes and be part of the future of phygital experiences.</p>
        <a href="/sponsor-deck" className="mt-6 inline-block bg-pink-600 py-2 px-4 text-white rounded">Download Sponsor Deck</a>
      </div>
    </section>
  );
};

const Register = () => {
  return (
    <section id="register" className="min-h-screen bg-blue-900 text-white flex items-center justify-center py-16">
      <div className="container mx-auto text-center">
        <h2 className="text-4xl font-bold mb-6">Register Now</h2>
        <p className="text-lg">Join us in shaping the future of immersive experiences. Secure your spot now and be a part of Cyberjam 2024.</p>
        <a href="/registration-form" className="mt-6 inline-block bg-pink-600 py-2 px-4 text-white rounded">Register</a>
      </div>
    </section>
  );
};

const Cyberjam2023 = () => {
  return (
    <section id="2023cyberjam" className="min-h-screen bg-gray-100 text-gray-900 flex items-center justify-center py-16">
      <div className="container mx-auto text-center">
        <h2 className="text-4xl font-bold mb-6 text-pink-600">Cyberjam 2023</h2>
        <p className="text-lg">Check out the highlights from Cyberjam 2023!</p>
        <div className="flex justify-center items-center mt-6">
          <iframe width="939" height="528" src="https://www.youtube.com/embed/Qu6LKDAfDZI" title="ETHChicago presents the 2023 CyberJam" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
        </div>
      </div>
    </section>
  );
}

export default App;