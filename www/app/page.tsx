export default function Home() {
  return (
    <main className="relative h-screen overflow-hidden text-[#201a17]">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-1/2 h-128 w-lg -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/60 blur-3xl" />
      </div>

      <div className="relative mx-auto flex h-screen max-w-108 px-4 py-6">
        <section className="relative flex flex-1 flex-col">
          <div className="flex-1" />

          <div className="pointer-events-none absolute inset-x-0 bottom-6">
            <div className="pointer-events-auto rounded-[30px] bg-[rgb(219_219_219_/0.92)] p-4 shadow-[0_18px_40px_rgba(78,62,49,0.14)] backdrop-blur-md">
              <textarea
                className="h-24 w-full resize-none bg-transparent text-base leading-7 text-[#2c2520] outline-none placeholder:text-[#8d8278]"
                placeholder="Write your thoughts..."
                defaultValue=""
              />

              <div className="mt-4 flex items-end justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <label className="relative">
                    <span className="sr-only">Choose author</span>
                    <select className="appearance-none rounded-full bg-black/8 px-4 py-2.5 pr-9 text-[15px] text-[#675c53] outline-none">
                      <option>Author</option>
                      <option>Marcus Aurelius</option>
                      <option>Seneca</option>
                      <option>Plato</option>
                      <option>All authors</option>
                    </select>
                    <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-[#8d8278]">
                      ˅
                    </span>
                  </label>
                </div>

                <button className="flex h-11 min-w-11 items-center justify-center rounded-full bg-white px-4 text-[#201a17] shadow-[0_8px_24px_rgba(255,255,255,0.24)]">
                  <span className="text-[26px] leading-none">↑</span>
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
