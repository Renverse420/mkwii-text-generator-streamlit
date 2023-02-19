import re

import streamlit as st
from PIL import Image, ImageChops, ImageEnhance


def main():
    st.set_page_config(
        page_title="MKWii Text Generator",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": None,
            "Report a bug": None,
            "About": "https://github.com/NOKKY726/mkwii-text-generator",
        },
    )

    if "top_color" not in st.session_state:
        st.session_state.top_color = "#f00"
        st.session_state.btm_color = "#0f0"
        st.session_state.colors = ["#fff" for _ in range(10000)]

    user_interface = UserInterface(
        st.sidebar.text_area("text_area", label_visibility="collapsed"),
        st.sidebar.slider("Brightness", step=5) / 50 + 1,  # 1.0 to 3.0
        st.sidebar.selectbox(
            "selectbox",
            ("Yellow", "White", "Color", "Colorful", "Gradient"),
            label_visibility="collapsed",
        ),
    )
    link = "[Developer's Twitter](https://twitter.com/nkfrom_mkw/)"
    st.sidebar.markdown(link, unsafe_allow_html=True)
    checkbox = st.sidebar.checkbox("Mobile")

    text_generator = TextGenerator(user_interface)
    MKWii_text = text_generator.generate_image()
    if not checkbox:
        st.image(MKWii_text)
    else:
        st.sidebar.image(MKWii_text)


class UserInterface:
    def __init__(self, text_area, slider, selectbox) -> None:
        self.file_names = self.to_file_names(text_area)
        self.slider = slider
        self.selectbox = selectbox
        self.radio = "Vertical"
        self.create_widget_if_needed()

    def to_file_names(self, text_area) -> list:
        replace_dict = {":": "CORON", ".": "PERIOD", "/": "SLASH", " ": "SPACE"}
        file_names = [replace_dict.get(char, char) for char in text_area.upper()]

        count, need_replace = 0, False  # 「'」間の文字を置換
        for i, file_name in enumerate(file_names):
            if file_name == "'" and count < file_names.count("'") // 2:
                if not need_replace:
                    need_replace = True
                else:
                    need_replace = False
                    count += 1
            elif need_replace and file_name in [*map(str, range(10)), "-", "SLASH", "SPACE"]:
                file_names[i] += "_"

        # 使用できない文字がないか検証
        file_names = [
            file_name
            for file_name in file_names
            if re.sub("[^-+0-9A-Z\n]", "", file_name)
        ]
        # 右側の空白と改行を削除
        while len(file_names) and file_names[-1] in ["SPACE", "SPACE_", "\n"]:
            del file_names[-1]

        return file_names

    def create_widget_if_needed(self) -> None:
        def set_top_color():
            st.session_state.top_color = st.session_state.color_picker_top

        def set_btm_color():
            st.session_state.btm_color = st.session_state.color_picker_btm

        if self.selectbox == "Color":
            st.session_state.color_picker_top = st.session_state.top_color
            st.sidebar.color_picker(
                "Pick a color", key="color_picker_top", on_change=set_top_color
            )
        elif self.selectbox == "Colorful" and len(self.file_names):
            col1, col2 = st.sidebar.columns((1, 2))
            with col2:
                index = st.selectbox(  # インデックスの取得
                    "Select the character",
                    range(len(self.file_names)),
                    format_func=lambda x: self.file_names[x],
                )

            def set_colors():
                st.session_state.colors[index] = st.session_state.color_picker_colorful

            with col1:
                st.session_state.color_picker_colorful = st.session_state.colors[index]
                st.color_picker(
                    "Pick a color", key="color_picker_colorful", on_change=set_colors
                )
        elif self.selectbox == "Gradient":
            self.radio = st.sidebar.radio(
                "radio", ("Vertical", "Horizontal"),
                horizontal=True, label_visibility="collapsed",
            )
            col3, col4 = st.sidebar.columns(2)
            with col3:
                st.session_state.color_picker_top = st.session_state.top_color
                st.color_picker(
                    "Top" if self.radio == "Vertical" else "Left",
                    key="color_picker_top", on_change=set_top_color,
                )
            with col4:
                st.session_state.color_picker_btm = st.session_state.btm_color
                st.color_picker(
                    "Bottom" if self.radio == "Vertical" else "Right",
                    key="color_picker_btm", on_change=set_btm_color,
                )


class TextGenerator:
    def __init__(self, user_interface) -> None:
        self.file_names = user_interface.file_names
        self.slider = user_interface.slider
        self.selectbox = user_interface.selectbox
        self.radio = user_interface.radio

    def create_images(self) -> list:
        images = []
        for file_name in self.file_names:
            if file_name == "\n":
                images.append("LF")  # LF: Line Feed (改行)
                continue

            if self.selectbox == "Yellow":
                images.append(Image.open(f"Fonts/Yellow/{file_name}.png"))
            else:
                images.append(Image.open(f"Fonts/White/{file_name}.png"))

        return images

    # https://stackoverflow.com/questions/32530345/pil-generating-vertical-gradient-image/
    def gradient(self, size: tuple[int, int], top_color, btm_color) -> Image:
        base = Image.new("RGBA", size, top_color)
        top = Image.new("RGBA", size, btm_color)
        mask = Image.new("L", size)
        mask_data, width, height = [], *size  # アンパック
        for y in range(height):
            mask_data.extend([int(255 * (y / height))] * width)
        mask.putdata(mask_data)
        base.paste(top, mask=mask)
        return base

    def multiply_char(self) -> list:
        images = self.create_images()
        # 「Colorful」と「Gradient(Vertical)」以外は早期リターン
        if not (
            self.selectbox in ["Colorful", "Gradient"] and self.radio == "Vertical"
        ):
            return images

        for i, image1 in enumerate(images):
            if image1 == "LF":
                continue

            if self.selectbox == "Colorful":
                image2 = Image.new("RGBA", image1.size, st.session_state.colors[i])
            elif self.selectbox == "Gradient":
                image2 = self.gradient(
                    image1.size, st.session_state.top_color, st.session_state.btm_color
                )
            images[i] = ImageChops.multiply(image1, image2)

        return images

    def adjust_x_coordinate(self, x, image_width, file_name) -> int:
        # 50: 0～9 & SLASH, 42: - & +
        if image_width in [50, 42] or file_name in ["PERIOD", "CORON"]:
            image_width -= 4
        else:
            image_width -= 12

        if file_name in ["T", "7_"]:
            image_width -= 6
        elif file_name in ["I", "M", "CORON"]:
            image_width -= 2
        elif file_name in ["L", "Q"]:
            image_width += 2

        x += image_width
        return x

    def concat_image(self) -> Image:
        images = self.multiply_char()
        y, is_LF = 0, False
        concated_image = Image.open("Fonts/Yellow/SPACE.png")  # エラー防止
        for i, image in enumerate(images):  # 画像の結合
            if image == "LF":  # 改行処理
                y += 64
                is_LF = True
                continue

            if i == 0 or is_LF:
                x = 0
                image_width = image.width
                file_name = self.file_names[i]
                if i == 0:  # 1文字目
                    concated_image = image
                elif is_LF:  # 改行直後
                    bg = Image.new(
                        "RGBA", (max(concated_image.width, image_width), y + 64)
                    )
                    bg.paste(concated_image)
                    bg.paste(image, (0, y))
                    concated_image = bg
                    is_LF = False
            else:
                x = self.adjust_x_coordinate(x, image_width, file_name)
                image_width = image.width
                file_name = self.file_names[i]
                bg = Image.new(
                    "RGBA", (max(concated_image.width, x + image_width), y + 64)
                )
                bg.paste(concated_image)
                fg = Image.new("RGBA", bg.size)
                fg.paste(image, (x, y))
                concated_image = Image.alpha_composite(bg, fg)

        return concated_image

    def multiply_str(self) -> Image:
        concated_image = self.concat_image()
        # 「Color」と「Gradient(Horizontal)」以外は早期リターン
        if not (self.selectbox == "Color" or self.radio == "Horizontal"):
            return concated_image

        if self.selectbox == "Color":
            image2 = Image.new("RGBA", concated_image.size, st.session_state.top_color)
        elif self.radio == "Horizontal":
            image2 = self.gradient(
                (concated_image.height, concated_image.width),
                st.session_state.top_color, st.session_state.btm_color,
            )
            image2 = image2.transpose(Image.Transpose.ROTATE_90)
        return ImageChops.multiply(concated_image, image2)

    def generate_image(self) -> Image:
        color_image = self.multiply_str()
        enhancer = ImageEnhance.Brightness(color_image)  # 輝度調整
        return enhancer.enhance(self.slider)


if __name__ == "__main__":
    main()
