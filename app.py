import os
import streamlit as st
from ImageProcessor import ImageProcessor
from ImageCaptionWriter import ImageCaptionWriter
from datetime import datetime
from pathlib import Path
import io

writing = ''

def get_downloads_folder():
    home = Path.home()
    downloads_folder = home / "Downloads"
    return downloads_folder

# def save_to_file(content, filename):
#     downloads_folder = get_downloads_folder()
#     if not downloads_folder.exists():
#             st.error(f"다운로드 폴더가 존재하지 않습니다. {downloads_folder}")
#             return
#     file_path = downloads_folder / (filename + ".txt")
#     try:
#         with open(file_path, "w", encoding='utf-8') as f:
#             f.write(content)
#         st.success(f"내용이 {file_path}에 저장되었습니다.")
#     except Exception as e:
#         st.error(f"파일 저장 중 오류 발생: {e}")

def main():
    global writing
    st.title("이미지 캡션/글/해시태그 생성")

    # 1) API 키 입력 받기
    openai_api_key = st.text_input("OpenAI API 키를 입력하세요:", type="password")
    if not openai_api_key:
        st.warning("OpenAI API 키를 입력해주세요.")
        return

    # 2) 이미지 업로드 받기
    uploaded_files = st.file_uploader("이미지를 업로드하세요", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

    if uploaded_files:
        if not os.path.exists("temp"):
            os.makedirs("temp")

    image_paths = []
    for uploaded_file in uploaded_files:
        image_path = os.path.join("temp", uploaded_file.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        image_paths.append(image_path)

    processor = ImageProcessor(openai_api_key)
    writer = ImageCaptionWriter(openai_api_key)
    
    # 3) 메타데이터와 캡션 출력
    image_data_list = []
    for image_path in image_paths:
        try:
            result = processor.process_image(image_path)
            image_data_list.append(result)
            st.image(image_path, caption=os.path.basename(image_path))
            st.write("<<<<<<<<<< 메타데이터 >>>>>>>>>>")
            if 'metadata' in result and 'labeled_exif' in result['metadata']:
                st.write(f"  라벨링된 EXIF : {result['metadata']['labeled_exif']}")
                st.write(f"  위치 정보 : {result['metadata']['location_info']}")
            else:
                st.write("  메타데이터가 없습니다.")
                
            st.write(f"<<<<<<<<<< 생성된 캡션 >>>>>>>>>>")
            st.write(f"{result['caption']}")
        except Exception as e:
            st.error(f"예상치 못한 오류 발생 : {e} - 이미지 처리를 건너뜁니다.")
            
    if (len(image_data_list) > 0):
        # 4) 캡션만 저장할지 글 생성할지 선택
        choice = st.radio("캡션만 저장하시겠습니까? 아니면 글을 생성하시겠습니까?", ("캡션만 저장", "글 생성"), index=None)

        if choice == '캡션만 저장':
            # 5-1) 캡션만 저장
            filename = st.text_input("저장할 파일 이름을 입력하세요 (확장자 제외):")
            
            if len(filename) > 0:
                if st.button("캡션 저장"):
                    content = ""
                    for data in image_data_list:
                        content += f"{os.path.basename(data['image_path'])}({data['image_path']})\n"
                        content += f"이미지에 대한 캡션: {data['caption']}\n\n"
                    # save_to_file(content, filename)
                    st.download_button(
                        label="파일 다운로드",
                        data = content,
                        file_name = filename + '.txt',
                        mime = "text/plain"
                    )

        elif choice == '글 생성':
            # 5-2) 글 생성 준비
            user_context = writer.get_user_context()
            writing_style = writer.get_writing_style()
            writing_length = writer.get_writing_length()
            temperature = writer.get_temperature()
            user_info = writer.get_user_info()
            
            story = ''
            filename = ''
            generate_hashtags = st.checkbox("해시태그를 생성하시겠습니까?")
            # generate_writing = st.button("글 생성", key="generate_writing")
            
            # st.write(f"generate_hashtags => {generate_hashtags}")
            # st.write(f"generate_writing => {generate_writing}")
            
            # 6) 글 생성
            story = writer.write_story(image_data_list, user_context, writing_style, writing_length, temperature, user_info)
            writing = story
            st.write(f"<<<<<<<<<< 생성된 글 >>>>>>>>>>")
            st.write(story)
                
            # st.write(f"writing => {len(writing)}")
                
            # 7) 해시태그 생성 여부
            if generate_hashtags:
                # 8-2) 해시태그 생성 및 모든 내용 저장
                hashtags = writer.generate_hashtags(story)
                st.write(f"<<<<<<<<<< 생성된 해시태그 >>>>>>>>>>")
                st.write(hashtags)
                
                filename = st.text_input("저장할 파일 이름을 입력하세요 (확장자 제외):", key="filename_hashtags")
                
                # if len(filename) > 0:
                
                    # if st.button("저장하기", key="save_hashtags"):
                content = ""
                for data in image_data_list:
                    content += f"{os.path.basename(data['image_path'])}({data['image_path']})\n"
                    content += f"이미지에 대한 캡션: {data['caption']}\n\n"
                content += f"글: {story}\n\n"
                content += f"해시태그: {hashtags}\n"
                # save_to_file(content, filename)
                st.download_button(
                    label="파일 다운로드",
                    data = content,
                    file_name = filename  + '.txt',
                    mime = "text/plain"
                )
            else:
                # 8-1) 글까지만 저장
                filename = st.text_input("저장할 파일 이름을 입력하세요 (확장자 제외):", key="filename_story")
                
                # if len(filename) > 0:
                
                    # if st.button("저장하기", key="save_story"):
                content = ""
                for data in image_data_list:
                    content += f"{os.path.basename(data['image_path'])}({data['image_path']})\n"
                    content += f"이미지에 대한 캡션: {data['caption']}\n\n"
                content += f"글: {story}\n"
                # save_to_file(content, filename)
                st.download_button(
                    label="파일 다운로드",
                    data = content,
                    file_name = filename  + '.txt',
                    mime = "text/plain"
                )
        else:
            st.warning("캡션만 저장, 글 생성 중 선택하시기 바랍니다.")

        # # 9) 프로그램 종료
        # st.write("프로그램을 종료합니다.")

if __name__ == "__main__":
    main()