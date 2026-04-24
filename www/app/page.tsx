"use client";

import { FormEvent, KeyboardEvent, useEffect, useState } from "react";
import { axios, fetchAuthors, submitQuery } from "@/lib/api";
import type { AuthorOption, QueryResponse, SourceHit } from "@/lib/api-types";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  authorKey?: string;
  sources?: SourceHit[];
};

const formatExcerpt = (excerpt: string) =>
  excerpt.replace(/\S{24,}/g, (token) => token.replace(/(.{10})/g, "$1 "));

export default function Home() {
  const [authors, setAuthors] = useState<AuthorOption[]>([]);
  const [question, setQuestion] = useState("");
  const [selectedAuthor, setSelectedAuthor] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Ask about Stoicism, ethics, politics, or mortality. I’ll answer from the indexed texts and separate the supporting passages below.",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadAuthors = async () => {
      try {
        setAuthors(await fetchAuthors());
      } catch {
        setError(
          "Couldn't load authors from the backend. You can still ask across all texts.",
        );
      }
    };

    void loadAuthors();
  }, []);

  const handleSubmit = async (event?: FormEvent<HTMLFormElement>) => {
    event?.preventDefault();

    const trimmedQuestion = question.trim();
    if (trimmedQuestion.length < 3 || isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: trimmedQuestion,
      authorKey: selectedAuthor || undefined,
    };

    setMessages((current) => [...current, userMessage]);
    setQuestion("");
    setError("");
    setIsLoading(true);

    try {
      const response: QueryResponse = await submitQuery({
        question: trimmedQuestion,
        author_key: selectedAuthor || null,
      });

      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.answer,
          sources: response.sources,
        },
      ]);
    } catch (submissionError) {
      let message = "Something went wrong while contacting the backend.";

      if (axios.isAxiosError(submissionError)) {
        const detail = submissionError.response?.data?.detail;
        if (typeof detail === "string" && detail.trim()) {
          message = detail;
        }
      }

      setError(message);
      setMessages((current) =>
        current.filter((messageItem) => messageItem.id !== userMessage.id),
      );
      setQuestion(trimmedQuestion);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextareaKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSubmit();
    }
  };

  return (
    <main className="relative h-screen overflow-hidden text-[#201a17]">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-1/2 h-128 w-lg -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/60 blur-3xl" />
      </div>

      <div className="relative mx-auto flex h-screen px-5 py-6 sm:px-6">
        <section className="relative flex flex-1 flex-col">
          <div className="flex-1 overflow-x-hidden overflow-y-auto pb-44 pt-8">
            <div className="mx-auto flex w-full max-w-5xl flex-col items-center gap-6">
              {messages.map((message) => (
                <article
                  key={message.id}
                  className={`${
                    message.role === "user"
                      ? "ml-auto w-fit max-w-[85%] rounded-[28px] bg-[rgb(255_255_255_/0.82)] px-5 py-4 text-[#4c4454] shadow-[0_14px_34px_rgba(126,111,154,0.12)] backdrop-blur-md"
                      : "w-full max-w-4xl text-[#4b4454]"
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    {message.role === "user" ? (
                      <span className="text-[11px] font-semibold uppercase tracking-[0.24em] text-[#a29aac]">
                        Question
                      </span>
                    ) : null}

                    {message.authorKey ? (
                      <span className="rounded-full bg-black/6 px-3 py-1 text-[11px] uppercase tracking-[0.16em] text-[#6f6259]">
                        {message.authorKey}
                      </span>
                    ) : null}
                  </div>

                  <p className="mt-3 whitespace-pre-wrap wrap-anywhere text-[15px] leading-7 sm:text-[17px]">
                    {message.content}
                  </p>

                  {message.sources?.length ? (
                    <div className="mt-6 min-w-0 border-t border-white/40 pt-4">
                      <div className="flex items-center justify-between gap-3">
                        <h2 className="font-(--font-space-grotesk) text-sm uppercase tracking-[0.18em] text-[#857d92]">
                          Sources
                        </h2>
                        <span className="text-[11px] uppercase tracking-[0.2em] text-[#9a91a7]">
                          {message.sources.length} passages
                        </span>
                      </div>

                      <div className="mt-4 grid gap-3">
                        {message.sources.map((source, index) => (
                          <section
                            key={`${source.source_file}-${source.page}-${index}`}
                            className="min-w-0 border-l-2 border-[#cdbde8] pl-4"
                          >
                            <div className="flex min-w-0 flex-col gap-1 text-sm text-[#70697d] sm:flex-row sm:items-center sm:justify-between sm:gap-4">
                              <p className="min-w-0 wrap-anywhere font-medium text-[#50495b]">
                                {source.author}{" "}
                                <span className="text-[#8b7869]">in</span>{" "}
                                {source.work}
                              </p>
                              <p className="min-w-0 wrap-anywhere">
                                {source.source_file}{" "}
                                <span className="text-[#b89a84]">•</span> page{" "}
                                {source.page}
                              </p>
                            </div>
                            <p className="mt-2 whitespace-pre-wrap break-all wrap-anywhere text-sm leading-6 text-[#5b5466]">
                              {formatExcerpt(source.excerpt)}
                            </p>
                          </section>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </article>
              ))}

              {isLoading ? (
                <div className="w-full max-w-4xl text-[#6b6477]">
                  <span className="inline-flex items-center gap-2 text-sm">
                    <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-[#a06d49]" />
                    Retrieving passages and composing the answer...
                  </span>
                </div>
              ) : null}
            </div>
          </div>

          <div className="pointer-events-none absolute inset-x-0 bottom-6">
            <div className="mx-auto w-full max-w-lg px-3">
              <form
                onSubmit={(event) => void handleSubmit(event)}
                className="pointer-events-auto rounded-[30px] bg-[rgb(219_219_219_/0.92)] p-4 shadow-[0_18px_40px_rgba(78,62,49,0.14)] backdrop-blur-md"
              >
                <textarea
                  className="h-24 w-full resize-none bg-transparent text-base leading-7 text-[#2c2520] outline-none placeholder:text-[#8d8278]"
                  placeholder="Write your thoughts..."
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  onKeyDown={handleTextareaKeyDown}
                  disabled={isLoading}
                />

                <div className="mt-4 flex items-end justify-between gap-3">
                  <div className="flex min-w-0 items-center gap-2.5">
                    <label className="relative">
                      <span className="sr-only">Choose author</span>
                      <select
                        className="appearance-none rounded-full bg-black/8 px-4 py-2.5 pr-9 text-[15px] text-[#675c53] outline-none"
                        value={selectedAuthor}
                        onChange={(event) =>
                          setSelectedAuthor(event.target.value)
                        }
                        disabled={isLoading}
                      >
                        <option value="">Author</option>
                        {authors.map((author) => (
                          <option key={author.key} value={author.key}>
                            {author.author}
                          </option>
                        ))}
                      </select>
                      <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-[#8d8278]">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="24"
                          height="24"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="lucide lucide-chevron-down-icon lucide-chevron-down"
                        >
                          <path d="m6 9 6 6 6-6" />
                        </svg>
                      </span>
                    </label>

                    {error ? (
                      <p className="text-sm text-[#a44d36]">{error}</p>
                    ) : null}
                  </div>

                  <button
                    type="submit"
                    className="flex h-11 min-w-11 items-center justify-center rounded-full bg-white px-4 text-[#201a17] shadow-[0_8px_24px_rgba(255,255,255,0.24)] disabled:cursor-not-allowed disabled:opacity-60"
                    disabled={isLoading || question.trim().length < 3}
                  >
                    <span className="text-[26px] leading-none">
                      {isLoading ? "…" : "↑"}
                    </span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
