from openai import OpenAI
import base64
from PIL import Image
import io

class ImageCaptionGenerator:
    def __init__(self, openai_api_key):
        self.client = OpenAI(api_key=openai_api_key)

    def generate_caption(self, image_path, metadata):
        try:
            # 이미지 열기 및 처리
            with Image.open(image_path) as img:
                # RGBA 모드인 경우 RGB로 변환
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # 이미지 크기 조정 (필요한 경우)
                max_size = (512, 512)  # OpenAI API 권장 최대 크기
                img.thumbnail(max_size, Image.LANCZOS)
                
                # 이미지를 JPEG 형식의 바이트 스트림으로 변환
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            prompt = f"""이 이미지를 설명해주세요. 다음 메타데이터도 참고하세요:
            날짜/시간: {metadata['labeled_exif'].get('Date/Time', 'N/A')}
            위치: {metadata['location_info'].get('full_address', 'N/A')}
            """

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 비전 모델 사용
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ],
                    }
                ],
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"캡션 생성 중 오류 발생: {e}")
            return "캡션을 생성할 수 없습니다."