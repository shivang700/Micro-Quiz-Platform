import shutil
from pathlib import Path

# Define the source directory and the output zip path
project_root = Path("/mnt/data/micro-quiz-platform")
output_zip = "/mnt/data/micro-quiz-platform.zip"

# Create the project directory structure
(project_root / "public/images").mkdir(parents=True, exist_ok=True)
(project_root / "src/pages/quizzes").mkdir(parents=True, exist_ok=True)
(project_root / "src/pages/quiz").mkdir(parents=True, exist_ok=True)
(project_root / "src/pages/api/quizzes").mkdir(parents=True, exist_ok=True)
(project_root / "src/pages/api/quiz").mkdir(parents=True, exist_ok=True)
(project_root / "src/styles").mkdir(parents=True, exist_ok=True)

# Define the file content based on the latest project state
files = {
    "package.json": '''{
  "name": "micro-quiz-platform",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "autoprefixer": "^10.4.14",
    "next": "13.4.12",
    "postcss": "^8.4.24",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "tailwindcss": "^3.3.2"
  }
}
''',
    "tailwind.config.js": '''module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: { extend: {} },
  plugins: []
};
''',
    "postcss.config.js": '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
''',
    "next.config.js": '''module.exports = {
  reactStrictMode: true,
};
''',
    "src/styles/globals.css": '''@tailwind base;
@tailwind components;
@tailwind utilities;
''',
    "src/pages/_app.js": '''import '../styles/globals.css';

export default function App({ Component, pageProps }) {
  return <Component {...pageProps} />;
}
''',
    "src/pages/index.js": '''import Head from 'next/head';
import Link from 'next/link';
import Image from 'next/image';

export async function getStaticProps() {
  const res = await fetch('http://localhost:3000/api/categories');
  const categories = await res.json();
  return { props: { categories } };
}

export default function Home({ categories }) {
  return (
    <>
      <Head>
        <title>Micro‑Quiz Platform</title>
        <meta name="description" content="Short, topic‑specific quizzes" />
      </Head>
      <main className="p-8 grid grid-cols-2 gap-4">
        {categories.map(cat => (
          <Link key={cat.id} href={`/quizzes/${cat.id}`}>
            <a className="flex items-center border rounded p-4 hover:shadow">
              <Image src={cat.icon} width={40} height={40} alt={cat.name} />
              <span className="ml-2 font-medium">{cat.name}</span>
            </a>
          </Link>
        ))}
      </main>
    </>
  );
}
''',
    "src/pages/quizzes/[category].js": '''import Head from 'next/head';
import Link from 'next/link';

export async function getServerSideProps({ params }) {
  const res = await fetch(`http://localhost:3000/api/quizzes/${params.category}`);
  const quizzes = await res.json();
  return { props: { category: params.category, quizzes } };
}

export default function CategoryPage({ category, quizzes }) {
  return (
    <>
      <Head>
        <title>{category} Quizzes</title>
        <meta name="description" content={`All quizzes in ${category}`} />
      </Head>
      <main className="p-8">
        <h1 className="text-2xl mb-4 capitalize">{category} Quizzes</h1>
        <ul className="list-disc list-inside space-y-2">
          {quizzes.map(q => (
            <li key={q.id}>
              <Link href={`/quiz/${q.id}`}>{q.title}</Link>
            </li>
          ))}
        </ul>
      </main>
    </>
  );
}
''',
    "src/pages/quiz/[id].js": '''import { useState } from 'react';

export async function getServerSideProps({ params }) {
  const res = await fetch(`http://localhost:3000/api/quiz/${params.id}`);
  const quiz = await res.json();
  return { props: { quiz } };
}

export default function QuizPage({ quiz }) {
  const [current, setCurrent] = useState(0);
  const [score, setScore] = useState(0);
  const [done, setDone] = useState(false);
  const question = quiz.questions[current];

  function handleAnswer(choice) {
    if (choice === question.correct) setScore(s => s + 1);
    if (current + 1 < quiz.questions.length) setCurrent(c => c + 1);
    else setDone(true);
  }

  return (
    <main className="p-8">
      <h1 className="text-xl mb-4">{quiz.title}</h1>
      {!done ? (
        <div>
          <p className="mb-2">{question.text}</p>
          <div className="space-x-2">
            {question.options.map(opt => (
              <button
                key={opt}
                onClick={() => handleAnswer(opt)}
                className="border rounded px-4 py-2 hover:bg-gray-100"
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <p className="text-lg">Your score: {score}/{quiz.questions.length}</p>
      )}
    </main>
  );
}
''',
    "src/pages/api/categories.js": '''export default function handler(req, res) {
  res.status(200).json([
    { id: 'history', name: 'History', icon: '/images/history.png' },
    { id: 'science', name: 'Science', icon: '/images/science.png' },
    { id: 'math', name: 'Math', icon: '/images/math.png' },
    { id: 'programming', name: 'Programming', icon: '/images/code.png' },
  ]);
}
''',
    "src/pages/api/quizzes/[category].js": '''const quizzesByCategory = {
  history: [ { id: 'h1', title: 'Ancient Civilizations' } ],
  science: [ { id: 's1', title: 'Basic Physics' } ],
  math: [ { id: 'm1', title: 'Algebra Basics' } ],
  programming: [ { id: 'p1', title: 'JavaScript Essentials' } ],
};

export default function handler(req, res) {
  const { category } = req.query;
  res.status(200).json(quizzesByCategory[category] || []);
}
''',
    "src/pages/api/quiz/[id].js": '''const quizData = {
  h1: {
    id: 'h1',
    title: 'Ancient Civilizations',
    questions: [
      {
        text: 'Who built the pyramids?',
        options: ['Romans', 'Egyptians', 'Greeks'],
        correct: 'Egyptians',
      },
    ],
  },
  s1: {
    id: 's1',
    title: 'Basic Physics',
    questions: [
      {
        text: 'What is the unit of force?',
        options: ['Joule', 'Pascal', 'Newton'],
        correct: 'Newton',
      },
    ],
  },
  m1: {
    id: 'm1',
    title: 'Algebra Basics',
    questions: [
      {
        text: 'What is x if 2x = 10?',
        options: ['5', '10', '2'],
        correct: '5',
      },
    ],
  },
  p1: {
    id: 'p1',
    title: 'JavaScript Essentials',
    questions: [
      {
        text: 'What keyword declares a variable?',
        options: ['const', 'function', 'return'],
        correct: 'const',
      },
    ],
  },
};

export default function handler(req, res) {
  const { id } = req.query;
  res.status(200).json(quizData[id]);
}
'''
}

# Write each file
for filepath, content in files.items():
    full_path = project_root / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content)

# Zip the folder
shutil.make_archive("/mnt/data/micro-quiz-platform", 'zip', project_root)

# Return the path to download
output_zip
