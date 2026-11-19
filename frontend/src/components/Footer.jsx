export default function Footer() {
  return (
    <footer className="mt-12 bg-[#808080]">
      <div className="mx-auto flex max-w-5xl flex-col items-center justify-between gap-2 px-6 py-3 text-sm text-white sm:flex-row">
        <p>© {new Date().getFullYear()} Studeal</p>
        <div className="flex flex-col items-center gap-1 sm:flex-row sm:gap-4">
          <a href="mailto:studeal.lviv@gmail.com" className="transition-colors hover:text-white hover:underline">
            studeal.lviv@gmail.com
          </a>
          <a href="tel:+380502484450" className="transition-colors hover:text-white hover:underline">
            +380 50 248 44 50
          </a>
        </div>
      </div>
    </footer>
  );
}
