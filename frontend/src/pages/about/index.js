import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const About = ({ updateOrders, orders }) => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Пищеблог - О проекте" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Привет!</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Что это за сайт?</h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Представляю вам проект, созданный во время обучения в Яндекс Практикуме.
              Этот проект — часть учебного курса, фронтенд проекта предоставлен в качестве исходных данных,
              бэкэнд же разработан самостоятельно и отредактирован в соответствии с рекомендациями и
              требованиями опытных ревьюеров и наставников.
            </p>
            <p className={styles.textItem}>
              Цель этого сайта — дать возможность пользователям создавать и хранить рецепты на онлайн-платформе.
              Кроме того, можно скачать список продуктов, необходимых для приготовления блюда, просмотреть
              рецепты друзей и добавить любимые рецепты в список избранных.
            </p>
            <p className={styles.textItem}>
              Чтобы использовать все возможности сайта — нужна регистрация.
              Проверка адреса электронной почты не осуществляется, вы можете ввести любой email.
              Использование введённого вами адреса для отправки каких-либо писем не предусмотрено,
              можете не переживать, что упустите какое-то важное сообщение :)
            </p>
            <p className={styles.textItem}>
              Заходите и делитесь своими любимыми рецептами!
            </p>
          </div>
        </div>
        <aside>
          <h2 className={styles.additionalTitle}>
            Ссылки
          </h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Код проекта находится тут - <a href="https://github.com/FuntikPiggy"
                                             className={styles.textLink}>Github</a>
            </p>
            <p className={styles.textItem}>
              Автор проекта: Гурин Валерий Сергеевич
            </p>
            <p className={styles.textItem}>
              Автор проекта: <a href="https://vk.com/FuntikPiggy" className={styles.textLink}>VK</a>, <a
                href="https://t.me/FuntikPiggy" className={styles.textLink}>Telegram</a>
            </p>
          </div>
        </aside>
      </div>

    </Container>
  </Main>
}

export default About

