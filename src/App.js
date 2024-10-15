import React, { useState } from "react";
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
      <SponsorSection />
    </div>
  );
};

const SponsorSection = () => {
    const [selectedTier, setSelectedTier] = useState(null);
    const [password, setPassword] = useState('');
    const [selectedGuide, setSelectedGuide] = useState(null);
  
    const handleTierSelect = (tier) => {
      setSelectedTier(tier);
      setPassword('');
      setSelectedGuide(null);
    };

    const handleSubmit = (e) => {
      e.preventDefault();
      const passwords = {
        'community': 'weloveyou',
        'silver': 'willcreatesart',
        'gold': 'chainlink'
      };
      if (password === passwords[selectedTier]) {
        setSelectedGuide(selectedTier);
      } else {
        alert('Incorrect password');
      }
      setPassword('');
    };
  
    const renderPasswordForm = () => (
      <form onSubmit={handleSubmit} className="mb-4">
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder={`Enter ${selectedTier} password`}
          className="px-4 py-2 border rounded mr-2"
        />
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
          Access Guide
        </button>
      </form>
    );
  
    return (
      <section id="sponsor-section" className="min-h-screen bg-gray-100 text-gray-900 flex items-center justify-center py-16">
        <div className="container mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">For Sponsors Only</h2>
          {selectedTier && !selectedGuide && renderPasswordForm()}
          {selectedGuide && (
            <div className="mt-8">
              {selectedGuide === 'community' && <CommunityGuide />}
              {selectedGuide === 'silver' && <SilverTierGuide />}
              {selectedGuide === 'gold' && <GoldTierGuide />}
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <button onClick={() => handleTierSelect('community')} className="bg-blue-500 text-white px-4 py-2 rounded">
              Community Partners
            </button>
            <button onClick={() => handleTierSelect('silver')} className="bg-blue-500 text-white px-4 py-2 rounded">
              Silver Tier
            </button>
            <button onClick={() => handleTierSelect('gold')} className="bg-blue-500 text-white px-4 py-2 rounded">
              Gold Tier
            </button>
          </div>
        </div>
      </section>
    );
  };
  
  const CommunityGuide = () => (
    <div className="text-left max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-4">Cyberjam 2024 Community Partner Guide</h2>
      <h3 className="text-2xl font-semibold mb-2">A One-of-a-Kind Collaborative Hackathon</h3>
      <p className="mb-4">
        Welcome to Cyberjam 2024! This unique hackathon is designed to foster multidisciplinary collaboration, creating immersive 2D & 3D physical + digital (phygital) experiences. As a Community Partner, you play a crucial role in making this event a success.
      </p>
      
      <h4 className="text-xl font-semibold mb-2">Important Dates:</h4>
      <ul className="list-disc list-inside mb-4">
        <li>Jammer Registration End (Hard Deadline): Oct 15</li>
        <li>Opening Ceremony: Oct 19</li>
        <li>Build Week: Oct 19-27</li>
        <li>Closing Ceremony & Showcase: Oct 27</li>
      </ul>
      
      <p className="mb-4">
        <strong>Location:</strong> Chicago 1871, 222 W Merchandise Mart Plaza #1212
      </p>
      <p className="mb-4">
        <strong>Useful Links:</strong> <a href="https://linktr.ee/cyberjam.art" className="text-blue-500 underline">linktr.ee/cyberjam.art</a>
      </p>
      
      <h4 className="text-xl font-semibold mb-2">How You Can Help as a Community Partner</h4>
      <ul className="list-disc list-inside mb-4">
        <li className="mb-2">
          <strong>October 9-13:</strong> Tap into your network with a few posts, quote retweets, or even direct messaging to people you think would enjoy Jamming With Us. Help us build our follower counts on X and Instagram.
        </li>
        <li className="mb-2">
          <strong>October 15-19:</strong> Drive attendance to our Opening Ceremony on October 19.
        </li>
        <li className="mb-2">
          <strong>Community Prize Pool:</strong> Consider donating $500 to our Community Prize Pool, 100% of which goes to Jammers by popular vote.
        </li>
        <li className="mb-2">
          <strong>Judging Opportunity:</strong> If you can make it to the Closing Ceremony & Showcase, apply to be a Judge.
        </li>
        <li className="mb-2">
          <strong>Promotional Material:</strong> Provide your preferred logo and a one-liner about what you do. We'd love to post about you!
        </li>
      </ul>
      
      <h4 className="text-xl font-semibold mb-2">Our Audience: Multidisciplinary Teams</h4>
      <p className="mb-2">Each Cyberjam team must include at least one of each of these roles:</p>
      <ol className="list-decimal list-inside mb-4">
        <li>Hardware engineer</li>
        <li>Software developer</li>
        <li>Musician/SFX artist</li>
        <li>Visual artist</li>
        <li>Wildcard (marketing, sales, bizdev, UI/UX designers)</li>
      </ol>
      
      <h4 className="text-xl font-semibold mb-2">Cyberjam Themes</h4>
      <p className="mb-2">Jammers will build and compose phygital experiences around our curated themes:</p>
      <ul className="list-disc list-inside mb-4">
        <li>Governance</li>
        <li>Sports/Gaming</li>
        <li>Fashion</li>
        <li>Security & Privacy</li>
        <li>AI</li>
      </ul>
      <p className="mb-4">Let us know which themes are most interesting to you!</p>
      
      <h4 className="text-xl font-semibold mb-2">Pop-up Installations at the Closing Ceremony</h4>
      <p className="mb-4">
        Each team's work will culminate in a creative pop-up experience that blends physical and digital elements. This showcase is a great opportunity to see innovation in action!
      </p>
      
      <h4 className="text-xl font-semibold mb-2">Partnership Opportunities</h4>
      <p className="mb-4">
        The event offers networking opportunities for sponsors, participants, and industry experts. Let us know if you plan to attend or if you'd like to connect with specific types of participants.
      </p>
      
      <h4 className="text-xl font-semibold mb-2">Social Cross-Promotion</h4>
      <p className="mb-4">
        Feel free to use any info from this guide, our most recent ETHChicago announcement, or our 1871 overview as inspiration for your posts. You can also simply use our logo, <a href="https://linktr.ee/cyberjam.art" className="text-blue-500 underline">linktr.ee/cyberjam.art</a>, and the important dates for a simple post. If you want to get creative, our design assets are available in the shared Drive.
      </p>
      <p className="mb-4">
  Follow and promote Cyberjam on social media:
  <ul className="list-disc list-inside mb-4">
    <li><a href="https://twitter.com/Cyberjam_Art" className="text-blue-500 underline">Twitter/X</a></li>
    <li><a href="https://www.instagram.com/cyberjam.art/" className="text-blue-500 underline">Instagram</a></li>
  </ul>
</p>
      
      <h4 className="text-xl font-semibold mb-2">Team Composition and Experience</h4>
      <p className="mb-4">
        Based on our successful 2023 hackathon, this event brings together experienced professionals and diverse teams to create innovative solutions. The expertise of our participants ensures dynamic, forward-thinking results.
      </p>
      
      <h4 className="text-xl font-semibold mb-2">Brand Activation</h4>
      <p className="mb-4">
        Partner brands can showcase their products within the hackathon themes through interactive, phygital experiences. If you're interested in this opportunity, let us know and we can discuss further!
      </p>
      
      <p className="mb-4 font-semibold">
        Jammer Registration Waitlist is now open. Encourage your network to sign up to Jam with Us!
      </p>
      
      <p className="mb-4">
        Contact: <a href="mailto:cyberjam.art@gmail.com" className="text-blue-500 underline">cyberjam.art@gmail.com</a>
      </p>
      
      <p className="font-semibold">
        Thank you for your support!<br />
        Tippi Fifestarr & The Cyberjam Team
      </p>
    </div>
  );
  
  const SilverTierGuide = () => (
    <div className="text-left max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-4">ACYL Silver Tier Sponsor Guide for Cyberjam 2024</h2>
      <h3 className="text-2xl font-semibold mb-2">A One-of-a-Kind Collaborative Hackathon</h3>
      <p className="mb-4">
        Thank you for joining Cyberjam 2024 as our esteemed Silver Tier sponsor! Your contribution is instrumental in making this event a success. This guide outlines how ACYL and Willcreatesart will participate in and benefit from this unique hackathon designed to foster multidisciplinary collaboration.
      </p>
      
      <h4 className="text-xl font-semibold mb-2">Important Dates:</h4>
      <ul className="list-disc list-inside mb-4">
        <li>Opening Ceremony: Oct 19</li>
        <li>Build Week: Oct 19-27</li>
        <li>Closing Ceremony & Showcase: Oct 27</li>
      </ul>
      
      <p className="mb-4">
        <strong>Location:</strong> Chicago 1871, 222 W Merchandise Mart Plaza #1212
      </p>
      <p className="mb-4">
        <strong>Useful Links:</strong> <a href="https://linktr.ee/cyberjam.art" className="text-blue-500 underline">linktr.ee/cyberjam.art</a>
      </p>
      
      <h4 className="text-xl font-semibold mb-2">Your Contribution: $3000 in Value</h4>
      <p className="mb-4">
        As our Silver Tier sponsor, ACYL is providing invaluable videography services through Willcreatesart. Here's what this entails:
      </p>
      <ol className="list-decimal list-inside mb-4">
        <li className="mb-2">
          <strong>Opening Ceremony Coverage (Oct 19)</strong>
          <ul className="list-disc list-inside ml-4">
            <li>Willcreatesart will be present from 11 AM to 4 PM (with the possibility of early departure)</li>
            <li>Capture key moments of the kickoff event</li>
          </ul>
        </li>
        <li className="mb-2">
          <strong>Speaking Opportunity</strong>
          <ul className="list-disc list-inside ml-4">
            <li>Brief presentation about the 2023 recap video</li>
            <li>Share insights on ACYL's journey since last year's Cyberjam</li>
            <li>Call to action for the Side Quest (get us good footage!)</li>
          </ul>
        </li>
        <li className="mb-2">
          <strong>2025 Trailer Production</strong>
          <ul className="list-disc list-inside ml-4">
            <li>Capture footage throughout the event for the 2025 Cyberjam Trailer</li>
            <li>Edit a 2-minute trailer and recap video, inspired by the Beastie Boys "Awesome; I F**king Shot That!" concert video/trailer (<a href="https://youtu.be/2iQ_IWMA3bQ" className="text-blue-500 underline">Watch here</a>)</li>
            <li>The trailer will debut at the Closing Ceremony on Oct 27</li>
          </ul>
        </li>
      </ol>
      
      <h4 className="text-xl font-semibold mb-2">Benefits as a Silver Tier Sponsor</h4>
      <ul className="list-disc list-inside mb-4">
        <li>Access to 1 Side Quest (a smaller challenge for teams): this can be "GIVE ME GOOD HORIZONTAL FOOTAGE OF YOUR TEAM BUILDING"</li>
        <li>Speaking opportunity at the Opening Ceremony</li>
        <li>Prominent event features</li>
        <li>Social Media mentions & logo placements</li>
        <li>Product placements & promotional spots</li>
      </ul>
      
      <h4 className="text-xl font-semibold mb-2">How You Can Help</h4>
      <ul className="list-disc list-inside mb-4">
        <li>Retweet <a href="https://x.com/Cyberjam_Art/status/1845605609766297733" className="text-blue-500 underline">this tweet</a> </li>
        <li>Promote Cyberjam on your social media channels (X, Instagram) from Oct 15-19</li>
        <li>Drive attendance to our Opening Ceremony on October 19</li>
        <li>If possible, have a representative attend the Closing Ceremony & Showcase</li>
      </ul>
      
      <h4 className="text-xl font-semibold mb-2">Audience & Themes</h4>
      <p className="mb-2">Cyberjam brings together multidisciplinary teams, each including:</p>
      <ol className="list-decimal list-inside mb-4">
        <li>Hardware engineer</li>
        <li>Software developer</li>
        <li>Musician/SFX artist</li>
        <li>Visual artist</li>
        <li>Wildcard (marketing, sales, bizdev, UI/UX designers)</li>
      </ol>
      
      <p className="mb-2">Teams will build phygital experiences around our curated themes:</p>
      <ul className="list-disc list-inside mb-4">
        <li>Governance</li>
        <li>Sports/Gaming</li>
        <li>Fashion</li>
        <li>Security & Privacy</li>
        <li>AI</li>
      </ul>
      
      <h4 className="text-xl font-semibold mb-2">Social Cross-Promotion</h4>
      <p className="mb-4">
        We'd love to feature ACYL on our social media! Please provide:
      </p>
      <ul className="list-disc list-inside mb-4">
        <li>Your preferred logo</li>
        <li>A one-liner about ACYL's mission</li>
        <li>Any specific hashtags you'd like us to use</li>
      </ul>
      <p className="mb-4">
        Feel free to use our logo, <a href="https://linktr.ee/cyberjam.art" className="text-blue-500 underline">linktr.ee/cyberjam.art</a>, and the important dates in your posts. Our design assets are available in the shared Drive.
      </p>
      
      <h4 className="text-xl font-semibold mb-2">ACYL's Unique Role</h4>
      <p className="mb-4">
        Your expertise in experimental and independent art aligns perfectly with Cyberjam's innovative spirit. We're excited to see how Willcreatesart's unique perspective will capture the essence of our event, blending the worlds of art and technology.
      </p>
      
      <p className="mb-4">
        Thank you for your support in making Cyberjam 2024 an unforgettable experience!
      </p>
      
      <p className="mb-4">
        Contact: <a href="mailto:cyberjam.art@gmail.com" className="text-blue-500 underline">cyberjam.art@gmail.com</a>
      </p>
      
      <p className="font-semibold">
        Tippi Fifestarr & The Cyberjam Team
      </p>
    </div>
  );
  
  const GoldTierGuide = () => (
    <div className="text-left max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-4">Cyberjam 2024 Gold Sponsor Guide</h2>
      <h3 className="text-2xl font-semibold mb-2">A One-of-a-Kind Collaborative Hackathon</h3>
      <p className="mb-4">
        Welcome to Cyberjam 2024! As our esteemed Gold Sponsor, you play a crucial role in bringing this unique, multidisciplinary hackathon to life. This guide provides an overview of your involvement and the exciting opportunities ahead.
      </p>
      
      <h4 className="text-xl font-semibold mb-2">Event Details:</h4>
      <ul className="list-disc list-inside mb-4">
        <li>Jammer Registration Deadline: Oct 15</li>
        <li>Opening Ceremony: Oct 19</li>
        <li>Build Week: Oct 19-27</li>
        <li>Closing Ceremony & Showcase: Oct 27</li>
      </ul>
      <p className="mb-4">
        <strong>Location:</strong> Chicago 1871, 222 W Merchandise Mart Plaza #1212
      </p>
      
      <h4 className="text-xl font-semibold mb-2">Your Gold Sponsor Benefits:</h4>
      <ul className="list-disc list-inside mb-4">
        <li>Exclusive branding across all event materials and activities</li>
        <li>Opportunity to sponsor two Main Quests for teams</li>
        <li>Host a workshop and deliver key speaking opportunities</li>
        <li>Tailored video showcase of your brand/product</li>
        <li>Product placements and promotional spots</li>
        <li>Access to top talent and innovative ideas</li>
      </ul>
      
      <h4 className="text-xl font-semibold mb-2">How You Can Engage:</h4>
      <ul className="list-disc list-inside mb-4">
        <li>Promote Cyberjam through your network (Oct 11-14)</li>
        <li>Drive attendance to the Opening Ceremony (Oct 15-19)</li>
        <li>Customize a Theme with a challenge for your brand</li>
        <li>Provide Developer Experts as Mentors (remote OK, Chicago preferred)</li>
        <li>Attend the Closing Ceremony & Showcase as a Judge</li>
      </ul>
      
      <h4 className="text-xl font-semibold mb-2">Social Media Promotion:</h4>
      <p className="mb-4">
        Help us amplify Cyberjam's reach by following and promoting on social media:
        <ul className="list-disc list-inside mb-4">
          <li><a href="https://twitter.com/Cyberjam_Art" className="text-blue-500 underline">Twitter/X</a></li>
          <li><a href="https://www.instagram.com/cyberjam.art/" className="text-blue-500 underline">Instagram</a></li>
        </ul>
      </p>
      
      <p className="mb-4">
        For a comprehensive breakdown of your Gold Sponsor role, benefits, and opportunities, please refer to our detailed <a href="https://docs.google.com/document/d/16H63_YJFcsqGAN1D_i9Gb4Oh47xcnI3AKWXtEWLRgBg/edit?usp=sharing" className="text-blue-500 underline">Gold Tier Sponsor Guide</a>.
      </p>
      
      <p className="mb-4">
        We're excited to work closely with you to make Cyberjam 2024 an unforgettable experience that showcases innovation, creativity, and the power of multidisciplinary collaboration.
      </p>
      
      <p className="mb-4">
        For any questions or to discuss your sponsorship further, please contact us at: <a href="mailto:cyberjam.art@gmail.com" className="text-blue-500 underline">cyberjam.art@gmail.com</a>
      </p>
      
      <p className="font-semibold">
        Thank you for your support!<br />
        Tippi Fifestarr & The Cyberjam Team
      </p>
    </div>
  );

const Navbar = () => {
  return (
    <nav className="sticky top-0 bg-gray-900 text-white py-1">
      <div className="container mx-auto flex justify-between items-center">
        <a href="#home" className="flex items-center justify-center md:w-20 w-16 md:h-20 h-16 rounded-full">
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
        <p className="text-lg mb-8">Cyberjam 2024 is an immersive hackathon taking place from October 19th to October 27th at <a href="https://1871.com/" target="_blank" rel="noopener noreferrer" className="underline">Chicago's global innovation hub, 1871</a>. Teams of 5 will work together on phygital experiences combining art, technology, and innovation across five thematic tracks:</p>
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
        <a href="https://forms.gle/xCEp1JVBSPCwhGJu7" target="_blank" rel="noopener noreferrer" className="mt-6 inline-block bg-pink-600 py-2 px-4 text-white rounded">
          Jammer Waitlist Registration
        </a>
        <p className="text-sm m-4">
          Not sure which role fits you best? You will have the chance to select your avatar and define your strengths after completing registration.
        </p>
        <p className="text-lg mb-8">Together, these multidisciplinary teams work beyond the digital realm to create installations that merge physical and digital worlds, fostering continued collaboration and community engagement.</p>
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
          <div className="max-w-3xl mx-auto">
            <p className="text-lg mb-4">
              In 2023, we launched our first Cyberjam event, known as the &lt;imnotHackathon&gt; BETA (alpha). This groundbreaking event brought together a diverse group of creators, technologists, and innovators to explore the intersection of art and technology.
            </p>
            <p className="text-lg mb-4">
              Key highlights of the imnothackathon included:
            </p>
            <ul className="list-disc list-inside mb-4 text-left">
              <li>Multidisciplinary teams collaborating on innovative projects</li>
              <li>Immersive experiences blending physical and digital elements</li>
              <li>Workshops and mentorship from industry experts</li>
              <li>A showcase of cutting-edge "phygital" prototypes</li>
            </ul>
            <p className="text-lg mb-6">
              The event's success laid the foundation for Cyberjam 2024, setting a new standard for collaborative hackathons in the Chicago tech and art scene.
            </p>
          </div>
          <p className="text-xl font-semibold mb-4">Check out the highlights from Cyberjam 2023!</p>
          <div className="flex justify-center items-center mt-6 mb-4">
            <iframe width="939" height="528" src="https://www.youtube.com/embed/Qu6LKDAfDZI" title="ETHChicago presents the 2023 CyberJam" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerPolicy="strict-origin-when-cross-origin" allowFullScreen></iframe>
          </div>
          <p className="text-lg mt-4">
            Special thanks to <a href="https://x.com/WillCreatesArt" target="_blank" rel="noopener noreferrer" className="text-blue-500 underline font-semibold">@WillCreatesArt</a> for filming and editing this amazing recap video, capturing the essence of our inaugural event!
          </p>
        </div>
      </section>
    );
  }

export default App;