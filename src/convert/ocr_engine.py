from pathlib import Path

import pdfplumber
import easyocr
import numpy as np
import cv2


class OCREngine:
    """
    Responsável exclusivamente por OCR.

    Funções:
    - Abrir PDF
    - Executar OCR
    - Detectar e corrigir rotação automaticamente
    - Retornar texto + score OCR

    NÃO:
    - Classifica
    - Renomeia
    - Salva arquivos
    """

    def __init__(self, resolution: int = 300):
        print("[INFO] Inicializando EasyOCR...")

        self.lang = "pt"
        self.reader = easyocr.Reader([self.lang])
        self.resolution = resolution

        # Ângulos testados automaticamente
        # 0° | 90° horário | -90° anti-horário | 180°
        self.rotation_angles = [0, 90, -90, 180]

    # =====================================================
    # EXTRAÇÃO DE TEXTO COM ROTAÇÃO
    # =====================================================
    def extract_text(self, pdf_path: Path) -> dict:
        """
        Retorna:
        {
            "text": str,
            "ocr_score": float,
            "rotation": int
        }
        """

        pdf_path = Path(pdf_path)

        full_text = []
        page_scores = []
        page_rotations = []

        with pdfplumber.open(str(pdf_path)) as pdf:
            total_pages = len(pdf.pages)

            for page_number, page in enumerate(pdf.pages, start=1):
                print(f"[INFO] Página {page_number}/{total_pages}")

                # ================================
                # 1️⃣ TEXTO DIGITAL
                # ================================
                text = page.extract_text()
                if text and len(text.strip()) > 30:
                    full_text.append(text)
                    page_scores.append(1.0)
                    page_rotations.append(0)
                    continue

                # ================================
                # 2️⃣ OCR COM ROTAÇÃO
                # ================================
                print("[OCR] Aplicando OCR com detecção de rotação...")

                page_img = page.to_image(resolution=self.resolution)
                img = np.array(page_img.annotated)

                best_text = ""
                best_score = 0.0
                best_angle = 0

                for angle in self.rotation_angles:
                    normalized = self._normalize_image(img)
                    rotated = self._rotate_image(normalized, angle)

                    results = self.reader.readtext(
                        rotated,
                        detail=1
                    )

                    texts = []
                    scores = []

                    for _, txt, conf in results:
                        if txt.strip():
                            texts.append(txt)
                            scores.append(conf)

                    if scores:
                        avg_score = sum(scores) / len(scores)
                        if avg_score > best_score:
                            best_score = avg_score
                            best_text = "\n".join(texts)
                            best_angle = angle

                full_text.append(best_text)
                page_scores.append(best_score)
                page_rotations.append(best_angle)

                print(
                    f"[OCR] Melhor rotação: {best_angle}° | "
                    f"Score: {best_score:.2f}"
                )

        final_text = "\n".join(full_text).strip()
        final_score = (
            sum(page_scores) / len(page_scores)
            if page_scores else 0.0
        )

        return {
            "text": final_text,
            "ocr_score": round(final_score, 3),
            "rotation": max(set(page_rotations), key=page_rotations.count)
        }

    # =====================================================
    # ROTAÇÃO DE IMAGEM
    # =====================================================
    @staticmethod
    def _rotate_image(image: np.ndarray, angle: int) -> np.ndarray:
        """
        Aplica rotação discreta usando OpenCV.
        """
        if angle == 0:
            return image
        elif angle == 90:
            return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == -90:
            return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:
            return cv2.rotate(image, cv2.ROTATE_180)

        return image

    # =====================================================
    # NORMALIZAÇÃO FASE 1
    # =====================================================
    @staticmethod
    def _normalize_image(image: np.ndarray) -> np.ndarray:
        """
        Normalização Fase 1:
        - Grayscale
        - Resize proporcional
        - Blur leve
        - Normalização de contraste
        """

        # 1️⃣ Converte para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 2️⃣ Aumenta levemente a resolução (melhora OCR)
        height, width = gray.shape
        gray = cv2.resize(
            gray,
            (width * 2, height * 2),
            interpolation=cv2.INTER_CUBIC
        )

        # 3️⃣ Remove ruído leve
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        # 4️⃣ Normaliza contraste
        normalized = cv2.normalize(
            blurred,
            None,
            alpha=0,
            beta=255,
            norm_type=cv2.NORM_MINMAX
        )

        return normalized