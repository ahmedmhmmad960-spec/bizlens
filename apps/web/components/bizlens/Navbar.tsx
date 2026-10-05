import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

export default function Navbar() {
  return (
    <header className="fixed inset-x-0 top-0 z-50">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6 lg:px-8">
        <Link
          href="/"
          className="text-[15px] font-semibold tracking-[-0.02em] text-[#F5F5F5]"
        >
          BizLens
        </Link>

        <nav className="flex items-center gap-6">
          <Link
            href="#"
            className="text-sm text-[#A1A7B0] transition-colors hover:text-[#F5F5F5]"
          >
            Docs
          </Link>

          <Link
            href="#"
            className="group flex items-center gap-1.5 text-sm text-[#A1A7B0] transition-colors hover:text-[#F5F5F5]"
          >
            GitHub
            <ArrowUpRight
              size={14}
              strokeWidth={1.8}
              className="transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
            />
          </Link>
        </nav>
      </div>
    </header>
  );
}
