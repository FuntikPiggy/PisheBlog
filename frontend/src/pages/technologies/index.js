import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Технологии</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Технологии, которые применены в этом проекте:</h2>
          <div className={styles.text}>
            <ul className={styles.textItem}>
              <li className={styles.textItem}>
                <a href="https://www.python.org/">Python</a>
              </li>
              <li className={styles.textItem}>
                <a href="https://www.djangoproject.com/">Django</a>
              </li>
              <li className={styles.textItem}>
                <a href="https://www.django-rest-framework.org/">Django REST Framework</a>
              </li>
              <li className={styles.textItem}>
                <a href="https://djoser.readthedocs.io/en/latest/index.html">Djoser</a>
              </li>
              <li className={styles.textItem}>
                <a href="https://www.postgresql.org/">PostgreSQL</a>
              </li>
              <li className={styles.textItem}>
                <a href="https://gunicorn.org/">Gunicorn 'Green Unicorn'</a>
              </li>
              <li className={styles.textItem}>
                <a href="https://nginx.org/ru/">NGINX</a>
              </li>
              <li className={styles.textItem}>
                А так же различные библиотеки для Django.
              </li>
            </ul>
          </div>
        </div>
      </div>

    </Container>
  </Main>
}

export default Technologies

