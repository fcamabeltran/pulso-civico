"use client";

import { useEffect } from "react";

type ImageLightboxProps = {
  alt: string;
  onClose: () => void;
  src: string;
};

export function ImageLightbox({ alt, onClose, src }: ImageLightboxProps) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [onClose]);

  return (
    <div aria-modal="true" className="image-lightbox" onClick={onClose} role="dialog">
      <button aria-label="Cerrar imagen ampliada" className="image-lightbox-close" onClick={onClose} type="button">
        ×
      </button>
      <img
        alt={alt}
        className="image-lightbox-image"
        onClick={(event) => event.stopPropagation()}
        src={src}
      />
    </div>
  );
}
