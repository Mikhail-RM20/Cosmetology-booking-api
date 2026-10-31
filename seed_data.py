from core import config_set, hash_password
from database import Category, Procedures, SessionLocal, User
from utils import WorkTokens


async def generate_base_table():
    async with SessionLocal() as session:
        category_list = [
            Category(name="Чистка лица"),
            Category(name="Пилинг"),
            Category(name="Инъекционные процедуры"),
            Category(name="Аппаратные процедуры"),
            Category(name="Уход за телом"),
        ]

        session.add_all(category_list)
        await session.flush()

        procedures_list = [
            # Уход за лицом.
            Procedures(
                category_id=category_list[0].id,
                name_procedures="Гигиеническая чистка лица",
                description="Базовое очищение кожи: демакияж, очищение, мягкая чистка, тонизирование и увлажнение",
                price=2500,
            ),
            Procedures(
                category_id=category_list[0].id,
                name_procedures="Ультразвуковая чистка лица",
                description="Очищение пор и удаление поверхностных загрязнений с помощью ультразвукового аппарата",
                price=3000,
            ),
            Procedures(
                category_id=category_list[0].id,
                name_procedures="Механическая чистка лица",
                description="Ручное удаление чёрных точек и камедонов после подготовки кожи",
                price=3500,
            ),
            Procedures(
                category_id=category_list[0].id,
                name_procedures="Комбинированная чистка лица",
                description="Ультразвуковая и механическая чистка: подходит при выраженных загрязнениях пор",
                price=4500,
            ),
            Procedures(
                category_id=category_list[0].id,
                name_procedures="Чистка лица с пилингом",
                description="Комплекс: очищение кожи, пилинг и завершающий уход",
                price=5000,
            ),
            Procedures(
                category_id=category_list[0].id,
                name_procedures="Экспресс-уход за лицом",
                description="Быстрое очищение, тонизирование, увлажнение и защита кожи",
                price=2000,
            ),
            Procedures(
                category_id=category_list[0].id,
                name_procedures="Уход для проблемной кожи",
                description="Очищение, успокаивающие маски и уход, направленный на снижение жирности и раздражения",
                price=4000,
            ),
            Procedures(
                category_id=category_list[0].id,
                name_procedures="Уход для сухой кожи",
                description="Мягкое очищение, питательные маски и восстановление защитного барьера кожи",
                price=3500,
            ),
            Procedures(
                category_id=category_list[0].id,
                name_procedures="Уход с эффектом сияния",
                description="Очищение, лёгкий пилинг, маска и сыворотка для более свежего вида кожи",
                price=4500,
            ),
            Procedures(
                category_id=category_list[0].id,
                name_procedures="Уход перед важным событием",
                description="Комплексное очищение, увлажнение, маска и финальный уход",
                price=5000,
            ),
            # Пилинг
            Procedures(
                category_id=category_list[1].id,
                name_procedures="Поверхностный пилинг",
                description="Деликатное обновление верхнего слоя кожи, подходит для первого знакомства с пилингами",
                price=3000,
            ),
            Procedures(
                category_id=category_list[1].id,
                name_procedures="Молочный пилинг",
                description="Мягкое отшелушивание и увлажнение, подходит для тусклой и обезвоженной кожи",
                price=3000,
            ),
            Procedures(
                category_id=category_list[1].id,
                name_procedures="Миндальный пилинг",
                description="Очищение и выравнивание тона кожи, обычно хорошо переносится чувствительной кожей",
                price=4000,
            ),
            Procedures(
                category_id=category_list[1].id,
                name_procedures="Салициловый пилинг",
                description="Очищение кожи, склонной к жирности, чёрным точкам и воспалениям",
                price=4500,
            ),
            Procedures(
                category_id=category_list[1].id,
                name_procedures="Азелаиновый пилинг",
                description="Уход за кожей с постакне, неровным тоном и склонностью к воспалениям",
                price=4500,
            ),
            Procedures(
                category_id=category_list[1].id,
                name_procedures="Карбоновый пилинг",
                description="Очищение кожи с угольным составом и аппаратной обработкой",
                price=3800,
            ),
            Procedures(
                category_id=category_list[1].id,
                name_procedures="Срединный пилинг",
                description="Более выраженное обновление кожи; проводится курсом и требует восстановления",
                price=7000,
            ),
            Procedures(
                category_id=category_list[1].id,
                name_procedures="Ретиноевый пилинг",
                description="Процедура для обновления кожи, выравнивания рельефа и улучшения её внешнего вида",
                price=8000,
            ),
            # Инъекционные процедуры
            Procedures(
                category_id=category_list[2].id,
                name_procedures="Мезотерапия лица",
                description="Введение косметологических коктейлей для увлажнения и улучшения состояния кожи",
                price=5000,
            ),
            Procedures(
                category_id=category_list[2].id,
                name_procedures="Мезотерапия области вокруг глаз",
                description="Уход за тонкой кожей вокруг глаз, направленный на увлажнение и улучшение внешнего вида",
                price=5500,
            ),
            Procedures(
                category_id=category_list[2].id,
                name_procedures="Мезотерапия волосистой части головы",
                description="Введение препаратов для ухода за кожей головы и состоянием волос",
                price=6000,
            ),
            Procedures(
                category_id=category_list[2].id,
                name_procedures="Биоревитализация лица",
                description="Введение препаратов на основе гиалуроновой кислоты для увлажнения кожи",
                price=8000,
            ),
            Procedures(
                category_id=category_list[2].id,
                name_procedures="Биоревитализация лица и шеи",
                description="Увлажняющий уход для кожи лица и шеи",
                price=11000,
            ),
            Procedures(
                category_id=category_list[2].id,
                name_procedures="Биоревитализация вокруг глаз",
                description="Уход за периорбитальной зоной препаратами с гиалуроновой кислотой",
                price=9000,
            ),
            Procedures(
                category_id=category_list[2].id,
                name_procedures="Плазмотерапия",
                description="Процедура с использованием плазмы пациента, проводится после консультации специалиста",
                price=10000,
            ),
            # Аппаратные процедуры
            Procedures(
                category_id=category_list[3].id,
                name_procedures="Микротоковая терапия лица",
                description="Мягкое аппаратное воздействие для улучшения тонуса кожи и лимфодренажа",
                price=3500,
            ),
            Procedures(
                category_id=category_list[3].id,
                name_procedures="RF-лифтинг лица",
                description="Аппаратная процедура для улучшения упругости и плотности кожи",
                price=6000,
            ),
            Procedures(
                category_id=category_list[3].id,
                name_procedures="RF-лифтинг лица и шеи",
                description="Комплексная зона: лицо и шея",
                price=8000,
            ),
            Procedures(
                category_id=category_list[3].id,
                name_procedures="Карбокситерапия лица",
                description="Аппаратная процедура с углекислым газом для улучшения внешнего вида кожи",
                price=3000,
            ),
            Procedures(
                category_id=category_list[3].id,
                name_procedures="Фонофорез с уходовым составом",
                description="Введение уходовых компонентов с помощью ультразвука",
                price=2500,
            ),
            Procedures(
                category_id=category_list[3].id,
                name_procedures="Криотерапия лица",
                description="Охлаждающая процедура для освежения и успокоения кожи",
                price=2500,
            ),
            Procedures(
                category_id=category_list[3].id,
                name_procedures="Лазерная биоревитализация",
                description="Аппаратная процедура для увлажнения и обновления кожи",
                price=6000,
            ),
            # Уход за телом
            Procedures(
                category_id=category_list[4].id,
                name_procedures="Чистка спины",
                description="Очищение кожи спины, удаление загрязнений и завершающий уход",
                price=5000,
            ),
            Procedures(
                category_id=category_list[4].id,
                name_procedures="Пилинг спины",
                description="Отшелушивающая процедура для более ровной и чистой кожи спины",
                price=4000,
            ),
            Procedures(
                category_id=category_list[4].id,
                name_procedures="Массаж лица",
                description="Расслабляющий массаж лица и шеи для улучшения внешнего вида кожи",
                price=2500,
            ),
            Procedures(
                category_id=category_list[4].id,
                name_procedures="Лимфодренажный массаж лица",
                description="Мягкий массаж для уменьшения отёчности и улучшения контуров лица",
                price=3000,
            ),
            Procedures(
                category_id=category_list[4].id,
                name_procedures="Обёртывание тела",
                description="Уходовая процедура для тела с выбранным составом",
                price=4000,
            ),
            Procedures(
                category_id=category_list[4].id,
                name_procedures="Прессотерапия",
                description="Аппаратный лимфодренажный массаж",
                price=3000,
            ),
        ]

        session.add_all(procedures_list)
        admin = User(
            name=config_set.admin_name,
            surname=config_set.admin_surname,
            phone=config_set.admin_phone,
            role=config_set.admin_role,
            hash_password=hash_password(config_set.admin_password),
            email=config_set.admin_email,
        )

        session.add(admin)
        await session.flush()

        # Генерируем access и refresh токены.
        # Внутри метода refresh сохраняется в token_users.
        work_tokens = WorkTokens()

        access_token, refresh_token = await work_tokens.pair_generation_access_refresh(
            db=session,
            id_user=admin.id,
        )

        await session.commit()
