# Wizard-game
Shoot game 
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using Microsoft.Xna.Framework.Media;
using System;
using System.Collections.Generic;

namespace Wizard_of_Wizards
{
    public class GameWorld : Game
    {
        private GraphicsDeviceManager graphics; //Premade
        private SpriteBatch spriteBatch;
        public static float gameScale = 0.6f; //We make screensize for game 
        public static float scaleOffset = 0.1f; // It's scale offset for game
        public static Vector2 screenSize; //Essential variables. (screensize is used to adjust various items)
        private Texture2D collisionTexture;
        private Texture2D map;    //It's for Texture2D background
        private SpriteFont text; //A single spritefront for the text (viewing score)
        public static int lives = 3; //We make static field for life
        public static int score;      //Static field for score
        private int highScore;        //Create field for highScore
        public static float speed;      //Make speed field
        private static bool start = false; //startmenu stuff
        public static bool sound = false; //Play soundeffects and music.
        private bool soundTap = true; //Used to prevent music spam.
        private Random random = new Random();

        private List<GameObject> gameObjects;        //List for all gameobjects
        private static List<GameObject> newObjects;  //List for new objects
        private static List<GameObject> deleteObjects; //List for delete objects

        Player player = new Player();   //We need just one player

        /// <summary>
        /// Gameworlds constructor
        /// </summary>
        public GameWorld()
        {
            graphics = new GraphicsDeviceManager(this);
            Content.RootDirectory = "Content";
            IsMouseVisible = true;

            screenSize = new Vector2(graphics.PreferredBackBufferWidth, graphics.PreferredBackBufferHeight);
        }
        /// <summary>
        /// Initialize methode
        /// </summary>
        protected override void Initialize()
        {
            GameScale();                                //We make here our screensize

            gameObjects = new List<GameObject>();
            newObjects = new List<GameObject>();
            deleteObjects = new List<GameObject>();

            gameObjects.Add(player);
            gameObjects.Add(new MonsterEnemy(player));//we need to add it for at move into player
            gameObjects.Add(new KnightEnemy(player));//we need to add it for at move into player
            gameObjects.Add(new KnightEnemyRightSide(player));//we need to add it for at move into player


            base.Initialize();
        }
        /// <summary>
        /// Method where we load our content
        /// </summary>
        protected override void LoadContent()
        {
            //Create a new SpriteBatch, which can be used to draw textures.
            spriteBatch = new SpriteBatch(GraphicsDevice);
            map = Content.Load<Texture2D>("map");  // Download background picture for our game
            collisionTexture = Content.Load<Texture2D>("CollisionTexture"); //Download collision texture
            text = Content.Load<SpriteFont>("File"); //Download sprite fond
            MediaPlayer.IsRepeating = true;          //Set MediaPlayer to true
            Song music = Content.Load<Song>("Background"); //Download music
            MediaPlayer.Play(music);                       //Create a MediaPlayer to play downloaded music
            MediaPlayer.Pause();                           //Start, and pause music. Toggable later in the code.

            //Create foreach loop for all GameObjects
            foreach (GameObject go in gameObjects)
            {
                go.LoadContent(Content);
            }
        }
        /// <summary>
        /// Method where we make our updates
        /// </summary>
        /// <param name="gameTime"></param>
        protected override void Update(GameTime gameTime)
        {   //Make here option to start game when we push Key B
            if (!start)
            {
                KeyboardState keyState = Keyboard.GetState();
                if (keyState.IsKeyDown(Keys.B))
                {
                    start = true;
                }
            }
            else
            {
                if (GamePad.GetState(PlayerIndex.One).Buttons.Back == ButtonState.Pressed || Keyboard.GetState().IsKeyDown(Keys.Escape))
                    Exit();
                gameObjects.AddRange(newObjects);
                newObjects.Clear();

                foreach (GameObject go in gameObjects)  //Main update loop
                {
                    go.Update(gameTime);//Call each subclasses' update method, wherein they call for Move and all sorts methods
                    foreach (GameObject item in gameObjects)//Collision checking loop
                    {
                        go.CheckCollision(item);
                    }
                }
                foreach (GameObject go in newObjects) //Add the new objects from AddObject method
                {
                    go.LoadContent(Content);
                    gameObjects.Add(go);
                }
                newObjects.Clear();
                foreach (GameObject go in deleteObjects)//Loop for delete objects on collision
                {
                    gameObjects.Remove(go);
                }
                deleteObjects.Clear();

                KeyboardState keyState = Keyboard.GetState();

                if (keyState.IsKeyDown(Keys.V) && soundTap == true) //Toggle music and sounds
                {
                    if (sound == false)
                    {
                        sound = true;
                    }
                    else
                    {
                        sound = false;
                    }
                    soundTap = false;

                    if (sound)
                    {
                        MediaPlayer.Resume(); //if sound on, resume playing
                    }
                    else
                    {
                        MediaPlayer.Pause(); //if off stop playing
                    }
                }
                if (keyState.IsKeyUp(Keys.V))
                {
                    soundTap = true; //prevent running each time.
                }

                if (lives < 1) //If dead, pause all logic in the game.
                {
                    if (score > highScore) //Set new highscore
                    {
                        highScore = score;
                    }

                    MediaPlayer.Pause();

                    if (keyState.IsKeyDown(Keys.R)) //Restart game
                    {
                        RestartGame();

                        if (sound)
                        {
                            MediaPlayer.Resume();
                        }
                    }
                }
            }
            base.Update(gameTime);
        }
        /// <summary>
        /// Main method where we draw all our game objects
        /// </summary>
        /// <param name="gameTime"></param>
        protected override void Draw(GameTime gameTime)
        {
            GraphicsDevice.Clear(Color.CornflowerBlue);
            //Tells the game to start drawing
            spriteBatch.Begin();
            //Draw our background picture
            spriteBatch.Draw(map, new Vector2(0, 0), null, Color.White, 0, Vector2.Zero, 1, SpriteEffects.None, 0);
            //Draw sprite font
            spriteBatch.DrawString(text, $"Score: {score}\nLives: {lives}\n\nSound (V): On", new Vector2(0, 0), Color.White);

            foreach (GameObject go in gameObjects)//Loop for draw gameObjects
            {
                go.Draw(spriteBatch);  //Draw all spriteBatch

                DrawCollisionBox(go);  //Draw collision box
            }

            if (lives < 1) //If dead, call EndScreen draw method.
            {
                EndScreen();  //Call method EndScreen
            }

            StartScreen(); //Draws the start screen (to avoid instantly losing life upon start)
            //Tells the game to stop drawing
            spriteBatch.End();

            base.Draw(gameTime);
        }
        /// <summary>
        /// Method to make screensize for our game
        /// </summary>
        void GameScale()
        {
            graphics.PreferredBackBufferWidth = (int)(2400 * gameScale); //1200
            graphics.PreferredBackBufferHeight = (int)(1400 * gameScale); //700
            graphics.ApplyChanges();
            screenSize.X = graphics.PreferredBackBufferWidth;
            screenSize.Y = graphics.PreferredBackBufferHeight;
        }
        /// <summary>
        /// Method to draw a collision box
        /// </summary>
        /// <param name="gameObject"></param>
        private void DrawCollisionBox(GameObject gameObject)
        {
            Rectangle collisionBox = gameObject.GetCollisionBox();
            Rectangle topLine = new Rectangle(collisionBox.X, collisionBox.Y, collisionBox.Width, 1);
            Rectangle bottomLine = new Rectangle(collisionBox.X, collisionBox.Y + collisionBox.Height, collisionBox.Width, 1);
            Rectangle rightLine = new Rectangle(collisionBox.X + collisionBox.Width, collisionBox.Y, 1, collisionBox.Height);
            Rectangle leftLine = new Rectangle(collisionBox.X, collisionBox.Y, 1, collisionBox.Height);

            spriteBatch.Draw(collisionTexture, topLine, null, Color.Red, 0, Vector2.Zero, SpriteEffects.None, 1);
            spriteBatch.Draw(collisionTexture, bottomLine, null, Color.Red, 0, Vector2.Zero, SpriteEffects.None, 1);
            spriteBatch.Draw(collisionTexture, rightLine, null, Color.Red, 0, Vector2.Zero, SpriteEffects.None, 1);
            spriteBatch.Draw(collisionTexture, leftLine, null, Color.Red, 0, Vector2.Zero, SpriteEffects.None, 1);
        }
        /// <summary>
        /// Method some we use when we want to add an object
        /// </summary>
        /// <param name="go"></param>
        public static void Instantiate(GameObject go)
        {
            newObjects.Add(go);
        }
        /// <summary>
        /// Method some we use when an object should be destroy
        /// </summary>
        /// <param name="go"></param>
        public static void Destroy(GameObject go)
        {
            deleteObjects.Add(go);
        }
        /// <summary>
        /// Method that is active when we start the game
        /// </summary>
        private void StartScreen()
        {
            if (!start)
            {
                //We write what we need to do to start game
                string stringTemp = "Press \"B\" to start";
                Vector2 stringSize = text.MeasureString(stringTemp);
                spriteBatch.DrawString(text, stringTemp, new Vector2(screenSize.X / 2 - stringSize.X,
                    screenSize.Y / 2 - 70 - stringSize.Y), Color.White, 0, Vector2.Zero, 2f, 0, 0);
            }
        }
        /// <summary>
        /// Method that we use when end game
        /// </summary>
        private void EndScreen()
        {
            //We have info efter end of game
            string stringTemp = $"      GAME OVER\n You Achived a score \n               {score}" +
                $"\n with a Maximum score \n               {highScore}";
            Vector2 stringSize = text.MeasureString(stringTemp);
            spriteBatch.DrawString(text, stringTemp, new Vector2(screenSize.X / 2 - stringSize.X,
                screenSize.Y / 2 - (int)(stringSize.Y * 1.5)), Color.White, 0, new Vector2(0, 0), 2f, 0, 0);
            stringTemp = "Press \"R\" to retry";
            stringSize = text.MeasureString(stringTemp);
            spriteBatch.DrawString(text, stringTemp, new Vector2(screenSize.X / 2 - stringSize.X,
                screenSize.Y / 2 + (int)(stringSize.Y * 2.5)), Color.Yellow, 0, new Vector2(0, 0), 2f, 0, 0);
        }
        /// <summary>
        /// Method some we use to restart game when we lost
        /// </summary>
        private void RestartGame()
        {
            Initialize();
            LoadContent();
            start = true;
            lives = 3;
            score = 0;
            EnemySpeed();
        }
        /// <summary>
        /// Create speed for all enemies
        /// </summary>
        public static void EnemySpeed()
        {
            Random random = new Random();
            while (GameWorld.lives > 0) //When player is alive
            {
                if (GameWorld.score >= 0 && GameWorld.score <= 50)
                {
                    GameWorld.speed = random.Next(1, 4);
                    break;                    
                }
                if (GameWorld.score > 50 && GameWorld.score <= 100)
                {
                    GameWorld.speed = random.Next(3, 6);
                    break;                   
                }
                if (GameWorld.score > 100 && GameWorld.score <= 150)
                {
                    GameWorld.speed = random.Next(5, 8);
                    break;                    
                }
                if (GameWorld.score > 150)
                {
                    GameWorld.speed = 10;
                    break;
                }
            }            
        }
    }
}
